# coding:utf-8
'''
author:wangyi
'''
import json
import re
import thulac

# 数据预处理类
class Preprocess:


    # 通过正则清理文本数据
    def clean_data_by_re(self,inf,name_dir):
        '''
        :param inf: 输入数据文件路径(str)
        :param name_dir: 姓名文件路径
        :return: res:清理后数据组成的list
        '''
        # 将姓氏和某/x组合成正则表达式
        with open(name_dir, encoding='utf-8') as f:
            fns = "".join([line.strip() for line in f.readlines()])
            fn = "[" + fns + "]" + "[1-9]*某+[甲乙丙丁午己庚辛壬癸]*" \
                 + "|[" + fns + "]" + "x+[甲乙丙丁午己庚辛壬癸]*"

        with open(inf,encoding='utf-8') as f:
            res = []
            for i,line in enumerate(f.readlines()):
                # 读取法律事实文本
                fact = json.loads(line)['fact']
                # 将文本中的时间统一替换成<TIME>
                fact = re.sub('[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日[0-9]{1,2}时许'
                              '|[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日.*?[0-9]{1,2}时许'
                              '|[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日.*?午'
                              '|[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日晚上'
                              '|[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日晚'
                              '|[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日凌晨'
                              '|[0-9]{4}年[0-9]{1,2}月[0-9]{1,2}日'
                              '|[0-9]{4}年[0-9]{1,2}月份到[0-9]{1,2}月份'
                              '|[0-9]{4}年[0-9]{1,2}月'
                              '|[0-9]{4}年', '<TIME>', fact)
                # 替换所有的18岁以下年龄为<CHILD>标识,替换所有的18岁以上为<AUDLT>标识
                fact = re.sub(r'(?<!\d)(1[8-9]|[2-9]\d|[1-9]\d\d)岁', '<AUDLT>', fact)
                fact = re.sub(r'(?<!\d)([1-9]|1[1-7]|未满.*?)岁', '<CHILD>', fact)
                # 替换金额
                # 分为九个等级,1000以下-1级,1~2k-2级,2~3k-3级,以此类推,最大边界是6万元以上
                fact = re.sub(r'(?<!\d)(\d|[1-9]\d|[1-9]\d\d)(\.\d{0,2}){0,1}余?元', '<ONE>', fact)
                fact = re.sub(r'(?<!\d)(1\d\d\d)(\.\d{0,2}){0,1}余?元', '<TWO>', fact)
                fact = re.sub(r'(?<!\d)(2\d\d\d)(\.\d{0,2}){0,1}余?元', '<THREE>', fact)
                fact = re.sub(r'(?<!\d)([3-4]\d\d\d)(\.\d{0,2}){0,1}余?元', '<FOUR>', fact)
                fact = re.sub(r'(?<!\d)([5-9]\d\d\d)(\.\d{0,2}){0,1}余?元', '<FIVE>', fact)
                fact = re.sub(r'(?<!\d)(1\d\d\d\d)(\.\d{0,2}){0,1}余?元', '<SIX>', fact)
                fact = re.sub(r'(?<!\d)(1|一)(\.\d{0,2}){0,1}余?万余?元', '<SIX>', fact)
                fact = re.sub(r'(?<!\d)([2-4]\d\d\d\d)(\.\d{0,2}){0,1}余?元', '<SEVEN>', fact)
                fact = re.sub(r'(?<!\d)([2-4]|[二两三四])(\.\d{0,2}){0,1}余?万余?元', '<SEVEN>', fact)
                fact = re.sub(r'(?<!\d)(5\d\d\d\d)(\.\d{0,2}){0,1}余?元', '<EIGHT>', fact)
                fact = re.sub(r'(?<!\d)(5|五)(\.\d{0,2}){0,1}余?万余?元', '<EIGHT>', fact)
                fact = re.sub(r'(?<!\d)([6-9]\d\d\d\d|[1-9]\d\d\d\d\d)(\.\d{0,2}){0,1}余?元', '<NINE>', fact)
                fact = re.sub(r'(?<!\d)([6-9]|[六七八九])(\.\d{0,2}){0,1}余?万余?元', '<NINE>', fact)
                fact = re.sub(r'(?<![二三四五六七八九])十余?万余?元', '<NINE>', fact)
                fact = re.sub(r'(?<![二三四五六七八九])十[一二三四五六七八九]余?万余?元', '<NINE>', fact)
                fact = re.sub(r'(?<!\d)([1-9]\d)(\.\d{0,2}){0,1}余?万余?元', '<NINE>', fact)
                fact = re.sub(r'(?<!\d)([二三四五六七八九])(\.\d{0,2}){0,1}十余?万余?元', '<NINE>', fact)
                fact = re.sub(r'(?<!\d)([二三四五六七八九])(\.\d{0,2}){0,1}十[一二三四五六七八九]余?万余?元', '<NINE>', fact)
                # 替换人名为<PERSON>
                fact = re.sub(fn, '<PERSON>', fact)
                # 去除标点符号
                fact = re.sub(r'[\s+\.\!\/_,$%^*(+\"\')]+|[+——()?【】“”！，。？、~@#￥%……&*（）《》；：×X]+', "", fact)
                res.append(fact)
                print(i+1,'finished')
            return res
    # 分词
    def cut_word(self,outf,facts=None,inf=None):
        '''

        :param res: 若不以文件形式传入,则传入待分词的list
        :param inf: 等待分词的文件
        :param outf 输出文件地址
        :return:
        '''
        thu = thulac.thulac(seg_only=True)
        if facts is None and inf is None:
            raise ValueError("res and inf should not be None at the same time! ")
        elif facts is None:
            facts = [line.strip() for line in open(inf,encoding='utf-8').readlines()]
        else:
            facts = facts
        out = open(outf,'w',encoding='utf-8')
        for i,fact in facts:
            # TODO: 根据不同任务将不同的标签一起写入文件输出
            out.write(thu.cut(fact.strip(),text=True)+'\n')
            out.flush()
            print(i,'finished word seg')
        out.close()

if __name__ == '__main__':

    preprocess = Preprocess()
    res = preprocess.clean_data_by_re('../datasets/data_train.json','../datasets/familyname.txt')
    preprocess.cut_word('../datasets/result.txt',res)