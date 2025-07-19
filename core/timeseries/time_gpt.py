
import io
from nixtla import NixtlaClient
from pandas import DataFrame
import pandas as pd
# from ..config import settings


class TimeGPT:
    def __init__(self):
        self.nixtla_client = NixtlaClient(
            api_key="nixak-udxfelH7ifcZqaWVJiY2PSIg0drPUkIFOiKX4fzjVm0RS9fKUilMqc6T1MTE7Wuf86TCBRC1la0YMIB2"
        )
        
    #预测有问题
    def predict(self, df: DataFrame, h: int = 12, freq: str = "MS", time_col: str = 'date', target_col='OT'):
        print("======================================这里执行了时序预测")
        time_fcst_df = self.nixtla_client.forecast(df=df, h=h, time_col=time_col, target_col=target_col)
        fig = self.nixtla_client.plot(df[-h*2:], time_fcst_df, time_col=time_col, target_col=target_col)
        buf = io.BytesIO()
        fig.savefig(buf, format='png')
        buf.seek(0)
        png_data = buf.getvalue()
        buf.close()
        return time_fcst_df, png_data

if __name__ == "__main__":
    df = pd.read_csv("https://doc.c2sagent.com/ETTh1.csv")
    predictor = TimeGPT()
    # 执行预测
    # df.reset_index(inplace=True)
    time_fcst_df, fig_data = predictor.predict(
        df=df,
        h=12,
        freq="MS",
        time_col="date",
        target_col="OT"
    )
    