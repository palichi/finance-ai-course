import os
import numpy as np
import pandas as pd
import gymnasium
from gymnasium import spaces


class StockTradingEnv(gymnasium.Env):
    """PPO 기반 주식 거래 강화학습 환경"""

    metadata = {'render_modes': ['human']}

    def __init__(self, df, window_size=20, initial_balance=10_000_000, transaction_fee=0.00015):
        super().__init__()

        self.df = df.reset_index(drop=True)
        self.window_size = window_size
        self.initial_balance = initial_balance
        self.transaction_fee = transaction_fee

        # 기능 2: 0=매도, 1=보유, 2=매수
        self.action_space = spaces.Discrete(3)

        # 기능 3: window_size*5(OHLCV 정규화) + 2(포지션비율, 누적수익률)
        obs_dim = window_size * 5 + 2
        self.observation_space = spaces.Box(
            low=-np.inf, high=np.inf, shape=(obs_dim,), dtype=np.float32
        )

        self.current_step = window_size
        self.balance = initial_balance
        self.shares_held = 0
        self.net_worth = initial_balance
        self.prev_net_worth = initial_balance

    def _get_observation(self):
        window = self.df.iloc[self.current_step - self.window_size:self.current_step]

        # 가격 정규화: 윈도우 첫날 종가 기준 상대비율
        base_price = window['close'].iloc[0]
        if base_price == 0:
            base_price = 1.0

        price_cols = ['open', 'high', 'low', 'close']
        normalized_prices = window[price_cols].values / base_price - 1.0

        # 거래량 정규화: 윈도우 내 평균 기준 상대비율
        avg_volume = window['volume'].mean()
        if avg_volume == 0:
            avg_volume = 1.0
        normalized_volume = (window['volume'].values / avg_volume - 1.0).reshape(-1, 1)

        # (window_size, 5) -> (window_size * 5,)
        ohlcv_flat = np.hstack([normalized_prices, normalized_volume]).flatten()

        # 포지션 비율: 주식 가치 / 총자산
        position_price = window['close'].iloc[-1]
        stock_value = self.shares_held * position_price
        position_ratio = stock_value / self.net_worth if self.net_worth > 0 else 0.0

        # 누적 수익률
        cumulative_return = (self.net_worth - self.initial_balance) / self.initial_balance

        obs = np.append(ohlcv_flat, [position_ratio, cumulative_return]).astype(np.float32)
        return obs

    def reset(self, seed=None, options=None):
        super().reset(seed=seed)

        self.current_step = self.window_size
        self.balance = self.initial_balance
        self.shares_held = 0
        self.net_worth = self.initial_balance
        self.prev_net_worth = self.initial_balance

        obs = self._get_observation()
        info = {
            'net_worth': self.net_worth,
            'balance': self.balance,
            'shares_held': self.shares_held,
            'price': self.df['close'].iloc[self.current_step - 1],
        }
        return obs, info

    def step(self, action):
        current_price = self.df['close'].iloc[self.current_step]

        if action == 2:  # 매수: 현금 전액으로 최대 주식수 매수
            if self.balance > 0:
                max_shares = int(self.balance / (current_price * (1 + self.transaction_fee)))
                if max_shares > 0:
                    cost = max_shares * current_price * (1 + self.transaction_fee)
                    self.balance -= cost
                    self.shares_held += max_shares

        elif action == 0:  # 매도: 보유 주식 전량 매도
            if self.shares_held > 0:
                revenue = self.shares_held * current_price * (1 - self.transaction_fee)
                self.balance += revenue
                self.shares_held = 0
        # action == 1: 보유, no-op

        self.current_step += 1

        # 새로운 종가로 net_worth 재계산 (경계 초과 방지)
        step_idx = min(self.current_step, len(self.df) - 1)
        new_price = self.df['close'].iloc[step_idx]
        self.net_worth = self.balance + self.shares_held * new_price

        # 기능 6: reward = 이번 스텝 net_worth 변화율
        reward = (self.net_worth - self.prev_net_worth) / self.prev_net_worth
        self.prev_net_worth = self.net_worth

        done = False
        truncated = False

        # 기능 7: 총자산이 초기 자본의 30% 이하면 페널티 + 조기 종료
        if self.net_worth <= self.initial_balance * 0.3:
            reward -= 1.0
            done = True

        # 기능 8: 데이터 끝에 도달하면 종료
        if self.current_step >= len(self.df) - 1:
            done = True

        obs = self._get_observation()
        info = {
            'net_worth': self.net_worth,
            'balance': self.balance,
            'shares_held': self.shares_held,
            'price': new_price,
        }

        return obs, reward, done, truncated, info

    def render(self):
        price = self.df['close'].iloc[min(self.current_step, len(self.df) - 1)]
        cumulative_return = (self.net_worth - self.initial_balance) / self.initial_balance * 100
        print(
            f"Step: {self.current_step:4d} | "
            f"Price: {price:10,.0f} | "
            f"Cash: {self.balance:14,.0f} | "
            f"Shares: {self.shares_held:6d} | "
            f"NetWorth: {self.net_worth:14,.0f} | "
            f"Return: {cumulative_return:+.2f}%"
        )


# 기능 10: 실습용 랜덤워크 기반 가상 일별 시세 데이터 생성 함수
# 실전에서는 이 함수를 실제 시세 데이터(KRX API, Yahoo Finance 등)로 교체하세요.
def generate_sample_price_data(n_days=1000, seed=42):
    np.random.seed(seed)

    daily_returns = np.random.randn(n_days) * 0.02
    close = 100_000 * np.exp(np.cumsum(daily_returns))

    daily_range = np.abs(np.random.randn(n_days)) * 0.015
    high = close * (1 + daily_range)
    low = close * (1 - daily_range)
    open_price = np.clip(close * (1 + np.random.randn(n_days) * 0.005), low, high)
    volume = np.maximum(
        np.abs(np.random.randn(n_days) * 500_000 + 1_000_000).astype(int), 1
    )

    return pd.DataFrame({
        'open': open_price,
        'high': high,
        'low': low,
        'close': close,
        'volume': volume,
    })


# 기능 11: PPO 모델 학습 함수
def train_ppo_trading_model(df, total_timesteps=50_000, model_save_path="./models/ppo_trading_model"):
    from stable_baselines3 import PPO
    from stable_baselines3.common.vec_env import DummyVecEnv
    from stable_baselines3.common.monitor import Monitor

    split_idx = int(len(df) * 0.8)
    train_df = df.iloc[:split_idx].reset_index(drop=True)
    test_df = df.iloc[split_idx:].reset_index(drop=True)

    print(f"학습 데이터: {len(train_df)}일 | 검증 데이터: {len(test_df)}일")

    def make_env():
        env = StockTradingEnv(train_df)
        return Monitor(env)

    train_env = DummyVecEnv([make_env])

    model = PPO("MlpPolicy", train_env, verbose=1)
    model.learn(total_timesteps=total_timesteps)

    save_dir = os.path.dirname(model_save_path)
    if save_dir:
        os.makedirs(save_dir, exist_ok=True)
    model.save(model_save_path)
    print(f"모델 저장 완료: {model_save_path}")

    return model, train_df, test_df


# 기능 12: 백테스트 함수
def backtest(model, test_df, window_size=20):
    env = StockTradingEnv(test_df, window_size=window_size)
    obs, _ = env.reset()
    done = False

    while not done:
        action, _ = model.predict(obs, deterministic=True)
        obs, _, done, _, _ = env.step(action)

    ppo_return = (env.net_worth - env.initial_balance) / env.initial_balance * 100

    bh_start = test_df['close'].iloc[window_size]
    bh_end = test_df['close'].iloc[-1]
    bh_return = (bh_end - bh_start) / bh_start * 100

    print("\n" + "=" * 50)
    print("백테스트 결과")
    print("=" * 50)
    print(f"PPO 거래 전략 수익률:  {ppo_return:+.2f}%")
    print(f"Buy & Hold 수익률:    {bh_return:+.2f}%")
    print(f"초과 수익률:          {ppo_return - bh_return:+.2f}%")
    print("=" * 50)

    return ppo_return, bh_return


if __name__ == "__main__":
    print("1) 가상 시세 데이터 생성 중...")
    df = generate_sample_price_data(n_days=1000, seed=42)
    print(f"   생성 완료: {len(df)}일치 데이터\n")

    print("2) PPO 모델 학습 중...")
    model, train_df, test_df = train_ppo_trading_model(
        df,
        total_timesteps=50_000,
        model_save_path="./models/ppo_trading_model",
    )

    print("\n3) 백테스트 실행 중...")
    ppo_return, bh_return = backtest(model, test_df)
