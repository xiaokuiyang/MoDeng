# encoding=utf-8
from AutoDailyOpt.Sub import cal_rsv_rank_sub
from DataSource.Data_Sub import get_k_data_JQ
from Experiment.CornerDetectAndAutoEmail.Sub import add_stk_index_to_df
from Experiment.Reseau.StdForReseau.Sub import get_single_stk_reseau_sub
from HuiCe.Sub import cal_today_ochl
from SDK.shelfSub import shelveP

if __name__ == '__main__':
	from DataSource.auth_info import *
	stk_code = '000001'

	# 准备数据
	df_5m = get_k_data_JQ(stk_code, count=48*40, freq='5m')
	df_5m['date'] = df_5m.apply(lambda x: str(x['datetime'])[:10], axis=1)
	df_day = get_k_data_JQ(stk_code, count=800).sort_values(by='date', ascending=True)

	# 增加必要index
	df_5m = add_stk_index_to_df(df_5m)

	i = len(df_5m) - 48*20

	# 大循环
	for idx in df_5m[48*20:].index:

		# 获取当天数据
		df_today = cal_today_ochl(df_5m.loc[:idx, :].tail(50))

		# 获取时间
		date = df_5m.loc[idx, 'date']

		# 获取该日期之前数天的数据
		df_day_data = df_day[df_day['date'] < date].tail(16)

		# 增加今天的数据
		df_day_complete = df_day_data.append(df_today, ignore_index=True)

		# df_day_complete = df_5m.loc[:idx, :].tail(20)

		# 计算rsv和波动情况
		df_5m.loc[idx, 'rsv'] = cal_rsv_rank_sub(df_day_complete, 4)
		df_5m.loc[idx, 'reseau'] = get_single_stk_reseau_sub(df_day_complete, slow=3, quick=6)
		i = i - 1
		print('还剩%d行' %i)

	# 将生成的数据序列化
	shelveP(df_5m, './temp_data/', stk_code+'huice')
	end = 0
