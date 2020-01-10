# coding=utf-8import jsonimport threadingimport pandas as pdimport wximport osfrom Config.AutoGenerateConfigFile import data_dirfrom Config.Sub import read_config, write_configfrom DataSource.Code2Name import name2code, code2namefrom Function.GUI.GUI_main.note_string import note_dengshen_welcome, total_cmdfrom Global_Value.file_dir import json_file_url, opt_recordfrom Global_Value.thread_lock import opt_record_locktry:	from Function.LSTM.AboutLSTM.Test.TomorrowPredict import predict_tomorrow_indexexcept Exception as e:	print('有关lstm相关的代码没有导入成功，相关功能将受限，具体原因：\n' + str(e))from pylab import *# opt_record.json文件读写锁from SDK.MyTimeOPT import get_current_datetime_stropt_record_file_url = data_dir + '\opt_record.json'def add_stk(kind, name, tc):	"""	增加持仓	:param name:	:param tc:	:return:	"""		# 判断输入的是代码是名称	if name.isdigit():		code = name	else:		code = name2code(name)		if code == '未知代码':			tc.AppendText(name + ':不识别的股票名字！请尝试使用股票代码！')			return	# 向配置文件中写入 增加持仓的stk代码	stk_now = read_config()[kind]	if code not in stk_now:		stk_now.append(code)		write_config(kind, stk_now)		tc.AppendText('增加“' + name + '”成功！')	else:		tc.AppendText('增加“' + name + '”失败！')def delete_stk(kind, name, tc):	"""	从持仓中删除	:param name:	:param tc:	:return:	"""	# 判断输入的是代码是名称	if name.isdigit():		code = name	else:		code = name2code(name)		if code == '未知代码':			tc.AppendText(name + ':不识别的股票名字！请尝试使用股票代码！')			return	# 向配置文件中删除 增加持仓的stk代码	stk_now = read_config()[kind]	if code in stk_now:		stk_now.remove(code)		write_config(kind, stk_now)		tc.AppendText('删除“' + name + '”成功！')	else:		tc.AppendText('删除“' + name + '”失败！原先关注列表中没有 ' + name)def cat_stk(kind, tc):	"""	查看相关stk列表	:param kind:	:return:	"""	stk_list = read_config()[kind]	stk_name = str([code2name(x) for x in stk_list])	tc.AppendText(stk_name.replace('[', '').replace(']', '').replace(',', '\n'))def input_analysis(input_str, tc):	tc.AppendText('\n\n')	if '增加持仓' in input_str:		ipt_split = input_str.split(' ')		# 向配置文件中写入 增加持仓的stk代码		add_stk(kind='buy_stk', name=ipt_split[1], tc=tc)	elif '删除持仓' in input_str:		ipt_split = input_str.split(' ')		# 向配置文件中写入 增加持仓的stk代码		delete_stk(kind='buy_stk', name=ipt_split[1], tc=tc)	elif '增加关注' in input_str:		ipt_split = input_str.split(' ')		# 向配置文件中写入 增加持仓的stk代码		add_stk(kind='concerned_stk', name=ipt_split[1], tc=tc)	elif '查看记录' in input_str:		ipt_split = input_str.split(' ')		# 画图该stk的操作记录		plot_opt(stk_code=name2code(ipt_split[1]), tc=tc, opt_record=opt_record)	elif '删除关注' in input_str:		ipt_split = input_str.split(' ')		delete_stk(kind='concerned_stk', name=ipt_split[1], tc=tc)	elif '查看关注' in input_str:		cat_stk(kind='concerned_stk', tc=tc)	elif '查看持仓' in input_str:		cat_stk(kind='buy_stk', tc=tc)	elif '预测明日大盘' in input_str:		# 启动数据处理线程，专用于处理数据，防止软件操作卡顿		index_predict_thread = threading.Thread(target=predict_tomorrow_index, args=(tc, False))		index_predict_thread.start()	elif '清理' == input_str:		tc.SetValue('')	elif '帮助' == input_str:		tc.AppendText(total_cmd)			elif ('买入' in input_str) | ('卖出' in input_str):		add_opt(input_str, opt_record_file_url, tc)			elif '查看b记录' in input_str:		cat_stk_opt_record(			input_str=input_str,			json_file_url=opt_record_file_url,			tc=tc)	else:		tc.AppendText('没听懂，请明示！')class DengShen(wx.Frame):	def __init__(self, parent, title):		super(DengShen, self).__init__(parent, title=title, size=(700, 500))		# 绑定关闭函数		self.Bind(wx.EVT_CLOSE, self.on_close, parent)		panel = wx.Panel(self)		hbox3 = wx.BoxSizer(wx.HORIZONTAL)		self.t3 = wx.TextCtrl(panel, size=(600, 1000), style=wx.TE_MULTILINE)		hbox3.Add(self.t3, 1, wx.EXPAND | wx.ALIGN_LEFT | wx.ALL, 5)		self.t3.Bind(wx.EVT_TEXT_ENTER, self.on_enter_pressed)		self.t3.SetBackgroundColour('Black'), self.t3.SetForegroundColour('Green')		panel.SetSizer(hbox3)		# 打印欢迎语		self.t3.AppendText('输入帮助查看详细用法\n')		self.Centre()		self.Show()		self.Fit()	def on_close(self, event):		print('进入关闭响应函数！')		global dengshen_on		dengshen_on = False		event.Skip()	def on_key_typed(self, event):		print(event.GetString())	def on_enter_pressed(self, event):		# 获取最后一行		input_str = event.GetString().split('\n')[-1]		try:			input_analysis(input_str, self.t3)			self.t3.AppendText('\n\n请输入命令：')		except Exception as e:			self.t3.AppendText('出错了，小神惶恐！原因：\n' + str(e))	def OnMaxLen(self, event):		print("Maximum length reached")def plot_opt(stk_code, opt_record, tc):	if len(opt_record) == 0:		tc.AppendText(code2name(stk_code) + '：没有操作记录！')		return	df = pd.DataFrame(opt_record).set_index('date_time')	# 筛选	df = df[df['stk_code'] == stk_code]	if df.empty:		tc.AppendText(code2name(stk_code) + '：没有操作记录！')	# 计算上下限	df['sale_pot'] = df.apply(lambda x: x['p_last'] + x['sale_reseau'], axis=1)	df['buy_pot'] = df.apply(lambda x: x['p_last'] + x['buy_reseau'], axis=1)	df.loc[:, ['p_last', 'p_now', 'buy_pot', 'sale_pot']].plot(style=['*', '*', '^--', '^--'])	plt.show()def cat_stk_opt_record(input_str, json_file_url, tc):	if opt_record_lock.acquire():		r = '未知错误'		try:			r = cat_stk_b_opt_sub(stk_name=input_str.split(' ')[1], json_file_url=json_file_url)		except Exception as e:			r = '读写opt_record.json文件失败！原因：\n' + str(e)		finally:			opt_record_lock.release()			tc.AppendText(r + '\n')def cat_stk_b_opt_sub(stk_name, json_file_url):	"""	:param stk_name:	:param json_file_url:	:return:	"""		# 已有文件，打开读取	if os.path.exists(json_file_url):		with open(json_file_url, 'r') as f:			opt_record = json.load(f)	else:		return '没有记录文件！'		if name2code(stk_name) not in opt_record.keys():		return '没有' + stk_name + '的数据！'		if len(opt_record[name2code(stk_name)]['b_opt']) == 0:		return stk_name + '没有操作记录！'		return pd.DataFrame(opt_record[name2code(stk_name)]['b_opt']).sort_values(by='p', ascending=False).loc[:,	       ['time', 'p', 'amount']].to_string()def add_opt(input_str, json_file_url, tc):		if opt_record_lock.acquire():		r = ['未知错误']		try:			r = add_opt_to_json_sub(input_str, json_file_url, tc)		except Exception as e:			r = ['读写opt_record.json文件失败！原因：\n' + str(e)]		finally:			opt_record_lock.release()			for str_ in r:				tc.AppendText(str_ + '\n')def add_opt_to_json_sub(input_str, json_file_url, tc):	# 返回字符串	return_str = []		# 已有文件，打开读取	if os.path.exists(json_file_url):		with open(json_file_url, 'r') as f:			opt_record = json.load(f)	else:		opt_record = {}		# 解析输入	stk_name, opt, amount, p = input_str.split(' ')	stk_code = name2code(stk_name)	p, amount = float(p), float(amount)		if stk_code in opt_record.keys():		opt_r_stk = opt_record[stk_code]	else:		opt_r_stk = {			'b_opt': [],			'p_last': None,			'threshold_satisfied_flag': True,			'total_earn': 0,			'last_prompt_point': -1		}		if opt == '买入':		opt_r_stk['b_opt'].append(dict(time=get_current_datetime_str(), p=p, amount=amount))		if opt == '卖出':		if len(opt_r_stk['b_opt']) > 0:			opt_r_stk, earn_this = sale_stk_sub(opt_r_stk, amount, p, tc)			return_str.append('earn：' + str(earn_this) + '\n')		opt_r_stk['p_last'] = p	opt_r_stk['threshold_satisfied_flag'] = True		# 保存数据	opt_record[stk_code] = opt_r_stk	with open(json_file_url, 'w') as f:		json.dump(opt_record, f)		# 返回	return return_strdef sale_stk_sub(stk_record, s_amount, s_p, tc):	"""	:param stk_record:	:return:	"""	opt_r_stk = stk_record	# 本次盈利	earn_this = 0	if len(opt_r_stk['b_opt']) > 0:		p_min = np.min([x['p'] for x in opt_r_stk['b_opt']])		opt_r_stk['b_opt'].sort(key=lambda x: x['p'] == p_min, reverse=False)		# 循环清算		while True:			if opt_r_stk['b_opt'][-1]['amount'] <= s_amount:				# 注销				b_pop = opt_r_stk['b_opt'].pop(-1)				# 清算				s_amount = s_amount - b_pop['amount']				# 计算盈利				earn_this = earn_this + b_pop['amount'] * (s_p - b_pop['p'])			else:				# 清算				opt_r_stk['b_opt'][-1]['amount'] = opt_r_stk['b_opt'][-1]['amount'] - s_amount				# 计算盈利				earn_this = earn_this + s_amount * (s_p - opt_r_stk['b_opt'][-1]['p'])				break			# 判断是否有			if len(opt_r_stk['b_opt']) < 1:				if s_amount > 0:					tc.AppendText('异常： 可卖标的数量超过持有量！\n')				break		opt_r_stk['total_earn'] = opt_r_stk['total_earn'] + earn_this	return opt_r_stk, earn_thisif __name__ == '__main__':	app = wx.App()	DengShen(None, '灯神')	app.MainLoop()