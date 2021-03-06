#!/usr/bin/env python3
# coding: utf-8
# File: CJOAbbrFullSpider.py
# Author: lxw
# Date: 5/19/17 4:39 PM
# Usage:
"""
892家公司简称不被公司全称包含的公司，分别看以简称和全称作为当事人进行爬取所得到的案例数目
"""

import calendar
import json
import random
import requests
import scrapy
import time
import urllib.parse

from Spiders.CJOAbbrFullSpider.CJOAbbrFullSpider.middlewares import RotateUserAgentMiddleware
from Spiders.CJOAbbrFullSpider.get_proxy import get_proxy
from Spiders.CJOAbbrFullSpider.CJOAbbrFullSpider import items
from Spiders.CJOAbbrFullSpider.utils import generate_logger


class CJOAbbrFullSpider(scrapy.Spider):
    name = "CJOAbbrFullSpider"
    cases_per_page = 5
    url = "http://wenshu.court.gov.cn/List/ListContent"
    # url = "http://xiujinniu.com/xiujinniu/index.php"   # Validating Host/Referer/User-Agent/Proxy. OK.
    abbr_full_dict = {
        "深房集团": "深圳经济特区房地产(集团)股份有限公司",
        "深桑达": "深圳市桑达实业股份有限公司",
        "国药一致": "国药集团一致药业股份有限公司",
        "富奥股份": "富奥汽车零部件股份有限公司",
        "深特力": "深圳市特力(集团)股份有限公司",
        "深天地": "深圳市天地(集团)股份有限公司",
        "深赤湾": "深圳赤湾港航股份有限公司",
        "深科技": "深圳长城开发科技股份有限公司",
        "深华发": "深圳中恒华发股份有限公司",
        "深深宝": "深圳市深宝实业股份有限公司",
        "平潭发展": "中福海峡（平潭）发展股份有限公司",
        "三毛派神": "兰州三毛实业股份有限公司",
        "京山轻机": "湖北京山轻工机械股份有限公司",
        "方大化工": "方大锦化化工科技股份有限公司",
        "中鼎股份": "安徽中鼎密封件股份有限公司",
        "南天信息": "云南南天电子信息产业股份有限公司",
        "深纺织": "深圳市纺织(集团)股份有限公司",
        "深南电": "深圳南山热电股份有限公司",
        "杭汽轮": "杭州汽轮机股份有限公司",
        "粤水电": "广东水电二局股份有限公司",
        "常铝股份": "江苏常铝铝业股份有限公司",
        "劲嘉股份": "深圳劲嘉集团股份有限公司",
        "天宝股份": "大连天宝绿色食品股份有限公司",
        "高乐股份": "广东高乐玩具股份有限公司",
        "泰尔股份": "泰尔重工股份有限公司",
        "兴森科技": "深圳市兴森快捷电路科技股份有限公司",
        "雅化集团": "四川雅化实业集团股份有限公司",
        "辉丰股份": "江苏辉丰农化股份有限公司",
        "百润股份": "上海百润投资控股集团股份有限公司",
        "盛通股份": "北京盛通印刷股份有限公司",
        "山东章鼓": "山东省章丘鼓风机股份有限公司",
        "豪迈科技": "山东豪迈机械科技股份有限公司",
        "青青稞酒": "青海互助青稞酒股份有限公司",
        "顺威股份": "广东顺威精密塑料股份有限公司",
        "慈铭体检": "慈铭健康体检管理集团股份有限公司",
        "天赐材料": "广州天赐高新材料股份有限公司",
        "光洋股份": "常州光洋轴承股份有限公司",
        "三圣股份": "重庆三圣实业股份有限公司",
        "红墙股份": "广东红墙新材料股份有限公司",
        "泰嘉股份": "湖南泰嘉新材料科技股份有限公司",
        "英联股份": "广东英联包装股份有限公司",
        "钧达股份": "海南钧达汽车饰件股份有限公司",
        "新宁物流": "江苏新宁现代物流股份有限公司",
        "奥克股份": "辽宁奥克化学股份有限公司",
        "中环装备": "中节能环保装备股份有限公司",
        "元力股份": "福建元力活性炭股份有限公司",
        "理邦仪器": "深圳市理邦精密仪器股份有限公司",
        "科恒股份": "江门市科恒实业股份有限公司",
        "银邦股份": "银邦金属复合材料股份有限公司",
        "迪森股份": "广州迪森热能技术股份有限公司",
        "鹏翎股份": "天津鹏翎胶管股份有限公司",
        "劲拓股份": "深圳市劲拓自动化设备股份有限公司",
        "京天利": "北京无线天利移动信息技术股份有限公司",
        "飞凯材料": "上海飞凯光电材料股份有限公司",
        "华舟应急": "湖北华舟重工应急装备股份有限公司",
        "华凯创意": "湖南华凯文化创意股份有限公司",
        "宝钢股份": "宝山钢铁股份有限公司",
        "上港集团": "上海国际港务(集团)股份有限公司",
        "哈高科": "哈尔滨高科技(集团)股份有限公司",
        "岷江水电": "四川岷江水利电力股份有限公司",
        "武汉控股": "武汉三镇实业控股股份有限公司",
        "联美控股": "联美量子股份有限公司",
        "中昌数据": "中昌大数据股份有限公司",
        "浦东建设": "上海浦东路桥建设股份有限公司",
        "金山股份": "沈阳金山能源股份有限公司",
        "盘江股份": "贵州盘江精煤股份有限公司",
        "粤泰股份": "广州粤泰集团股份有限公司",
        "航发科技": "中国航发航空科技股份有限公司",
        "青松建化": "新疆青松建材化工(集团)股份有限公司",
        "柳化股份": "柳州化工股份有限公司",
        "信威集团": "北京信威科技集团股份有限公司",
        "中国动力": "中国船舶重工集团动力股份有限公司",
        "上海能源": "上海大屯能源股份有限公司",
        "山东药玻": "山东省药用玻璃股份有限公司",
        "前锋股份": "成都前锋电子股份有限公司",
        "运盛医疗": "运盛（上海）医疗科技股份有限公司",
        "天津磁卡": "天津环球磁卡股份有限公司",
        "钱江生化": "浙江钱江生物化学股份有限公司",
        "星湖科技": "广东肇庆星湖生物科技股份有限公司",
        "哈投股份": "哈尔滨哈投投资股份有限公司",
        "贵绳股份": "贵州钢绳股份有限公司",
        "广西广电": "广西广播电视信息网络股份有限公司",
        "赤峰黄金": "赤峰吉隆黄金矿业股份有限公司",
        "科达股份": "科达集团股份有限公司",
        "中国一重": "中国第一重型机械股份公司",
        "吉鑫科技": "江苏吉鑫风能科技股份有限公司",
        "君正集团": "内蒙古君正能源化工集团股份有限公司",
        "皖新传媒": "安徽新华传媒股份有限公司",
        "中国交建": "中国交通建设股份有限公司",
        "中国核电": "中国核能电力股份有限公司",
        "天鹅股份": "山东天鹅棉业机械股份有限公司",
        "川仪股份": "重庆川仪自动化股份有限公司",
        "森特股份": "森特士兴集团股份有限公司",
        "快克股份": "常州快克锡焊股份有限公司",
        "杰克股份": "杰克缝纫机股份有限公司",
        "徕木股份": "上海徕木电子股份有限公司",
        "清源股份": "清源科技（厦门）股份有限公司",
        "龙韵股份": "上海龙韵广告传播股份有限公司",
        "四通股份": "广东四通集团股份有限公司",
        "铁流股份": "浙江铁流离合器股份有限公司",
        "汇丽股份": "上海汇丽建材股份有限公司",
        "凌云科技": "上海凌云实业发展股份有限公司",
        "大化股份": "大化集团大连化工股份有限公司",
        "伊煤股份": "内蒙古伊泰煤炭股份有限公司",
        "锦江股份": "上海锦江国际酒店发展股份有限公司",
        "锦旅股份": "上海锦江国际旅游股份有限公司",
        "上海物贸": "上海物资贸易股份有限公司",
        "百联股份": "上海百联集团股份有限公司",
        "丹化科技": "丹化化工科技股份有限公司",
        "上柴股份": "上海柴油机股份有限公司",
        "海欣股份": "上海海欣集团股份有限公司",
        "锦江投资": "上海锦江国际实业投资股份有限公司",
        "浦东金桥": "上海金桥出口加工区开发股份有限公司",
        "海立股份": "上海海立(集团)股份有限公司",
        "读者传媒": "读者出版传媒股份有限公司",
        "继峰股份": "宁波继峰汽车零部件股份有限公司",
        "洛阳钼业": "洛阳栾川钼业集团股份有限公司",
        "至正股份": "上海至正道化高分子材料股份有限公司",
        "麦迪科技": "苏州麦迪斯顿医疗科技股份有限公司",
        "恒润股份": "江阴市恒润重工股份有限公司",
        "国泰集团": "江西国泰民爆集团股份有限公司",
        "银龙股份": "天津银龙预应力材料股份有限公司",
        "醋化股份": "南通醋酸化工股份有限公司",
        "百利科技": "湖南百利工程科技股份有限公司",
        "哈森股份": "哈森商贸（中国）股份有限公司",
        "益丰药房": "益丰大药房连锁股份有限公司",
        "亚翔集成": "亚翔系统集成科技（苏州）股份有限公司",
        "兴业股份": "苏州兴业材料科技股份有限公司",
        "合诚股份": "合诚工程咨询集团股份有限公司",
        "中持股份": "中持水务股份有限公司",
        "城地股份": "上海城地建设股份有限公司",
        "新澳股份": "浙江新澳纺织股份有限公司",
        "元祖股份": "上海元祖梦果子股份有限公司",
        "能科股份": "能科节能技术股份有限公司",
        "正平股份": "正平路桥建设股份有限公司",
        "坤彩科技": "福建坤彩材料科技股份有限公司",
        "神力股份": "常州神力电机股份有限公司",
        "道森股份": "苏州道森钻采设备股份有限公司",
        "新日股份": "江苏新日电动车股份有限公司",
        "威龙股份": "威龙葡萄酒股份有限公司",
        "常青股份": "合肥常青机械股份有限公司",
        "泰晶科技": "湖北泰晶电子科技股份有限公司",
        "德宏股份": "浙江德宏汽车电子电器股份有限公司",
        "纽威股份": "苏州纽威阀门股份有限公司",
        "航天工程": "航天长征化学工程股份有限公司",
        "至纯科技": "上海至纯洁净系统科技股份有限公司",
        "皖天然气": "安徽省天然气开发股份有限公司",
        "镇海股份": "镇海石化工程股份有限公司",
        "杭电股份": "杭州电缆股份有限公司",
        "茶花股份": "茶花现代家居用品股份有限公司",
        "诺力股份": "诺力机械股份有限公司",
        "广信股份": "安徽广信农化股份有限公司",
        "口子窖": "安徽口子酒业股份有限公司",
        "高能环境": "北京高能时代环境技术股份有限公司",
        "永艺股份": "永艺家具股份有限公司",
        "苏利股份": "江苏苏利精细化工股份有限公司",
        "立霸股份": "江苏立霸实业股份有限公司",
        "思维列控": "河南思维自动化设备股份有限公司",
        "韦尔股份": "上海韦尔半导体股份有限公司",
        "集友股份": "安徽集友新材料股份有限公司",
        "亚振家居": "亚振家具股份有限公司",
        "元成股份": "浙江元成园林集团股份有限公司",
        "新天然气": "新疆鑫泰天然气股份有限公司",
        "华达科技": "华达汽车科技股份有限公司",
        "吴江银行": "江苏吴江农村商业银行股份有限公司",
        "派思股份": "大连派思燃气系统股份有限公司",
        "福鞍股份": "辽宁福鞍重工股份有限公司",
        "华懋科技": "华懋(厦门)新材料科技股份有限公司",
        "华铁科技": "浙江华铁建筑安全科技股份有限公司",
        "井神股份": "江苏井神盐化股份有限公司",
        "应流股份": "安徽应流机电股份有限公司",
        "海天味业": "佛山市海天调味食品股份有限公司",
        "松发股份": "广东松发陶瓷股份有限公司",
        "诺邦股份": "杭州诺邦无纺股份有限公司",
        "天龙股份": "宁波天龙电子股份有限公司",
        "恒通股份": "恒通物流股份有限公司",
        "日月股份": "日月重工股份有限公司",
        "九华旅游": "安徽九华山旅游发展股份有限公司",
        "亚邦股份": "江苏亚邦染料股份有限公司",
        "新泉股份": "江苏新泉汽车饰件股份有限公司",
        "圣龙股份": "宁波圣龙汽车动力系统股份有限公司",
        "兰石重装": "兰州兰石重型装备股份有限公司",
        "腾龙股份": "常州腾龙汽车零部件股份有限公司",
        "翠微股份": "北京翠微大厦股份有限公司",
        "华贸物流": "港中旅华贸国际物流股份有限公司",
        "共进股份": "深圳市共进电子股份有限公司",
        "万林股份": "江苏万林现代物流股份有限公司",
        "宏盛股份": "无锡宏盛换热器制造股份有限公司",
        "海汽集团": "海南海汽运输集团股份有限公司",
        "振华股份": "湖北振华化学股份有限公司",
        "国检集团": "中国建材检验认证集团股份有限公司",
        "永吉股份": "贵州永吉印务股份有限公司",
        "华立股份": "东莞市华立实业股份有限公司",
        "凯众股份": "上海凯众材料科技股份有限公司",
        "如通股份": "江苏如通石油机械股份有限公司",
        "常熟汽饰": "常熟市汽车饰件股份有限公司",
        "三维股份": "浙江三维橡胶制品股份有限公司",
        "德新交运": "德力西新疆交通运输集团股份有限公司",
        "全筑股份": "上海全筑建筑装饰集团股份有限公司",
        "威帝股份": "哈尔滨威帝电子股份有限公司",
        "爱普股份": "爱普香料集团股份有限公司",
        "中科曙光": "曙光信息产业股份有限公司",
        "中设集团": "中设设计集团股份有限公司",
        "花王股份": "花王生态工程股份有限公司",
        "晶方科技": "苏州晶方半导体科技股份有限公司",
        "联明股份": "上海联明机械股份有限公司",
        "奥康国际": "浙江奥康鞋业股份有限公司",
        "丰林集团": "广西丰林木业集团股份有限公司",
        "大唐发电": "大唐国际发电股份有限公司",
        "中国重工": "中国船舶重工股份有限公司",
        "金钼股份": "金堆城钼业股份有限公司",
        "中国汽研": "中国汽车工程研究院股份有限公司",
        "凤凰传媒": "江苏凤凰出版传媒股份有限公司",
        "中远海控": "中远海运控股股份有限公司",
        "南方传媒": "南方出版传媒股份有限公司",
        "江河集团": "江河创建集团股份有限公司",
        "中远海发": "中远海运发展股份有限公司",
        "中国科传": "中国科技出版传媒股份有限公司",
        "招商轮船": "招商局能源运输股份有限公司",
        "中海油服": "中海油田服务股份有限公司",
        "蓝科高新": "甘肃蓝科石化高新装备股份有限公司",
        "力帆股份": "力帆实业(集团)股份有限公司",
        "郑煤机": "郑州煤矿机械集团股份有限公司",
        "风范股份": "常熟风范电力设备股份有限公司",
        "潞安环能": "山西潞安环保能源开发股份有限公司",
        "星宇股份": "常州星宇车灯股份有限公司",
        "中国电建": "中国电力建设股份有限公司",
        "滨化股份": "滨化集团股份有限公司",
        "平煤股份": "平顶山天安煤业股份有限公司",
        "中国中冶": "中国冶金科工股份有限公司",
        "中国核建": "中国核工业建设股份有限公司",
        "中国太保": "中国太平洋保险(集团)股份有限公司",
        "东风股份": "汕头东风印刷股份有限公司",
        "通用股份": "江苏通用科技股份有限公司",
        "怡球资源": "怡球金属资源再生(中国)股份有限公司",
        "湘油泵": "湖南机油泵股份有限公司",
        "利群股份": "青岛利群百货集团股份有限公司",
        "新华保险": "新华人寿保险股份有限公司",
        "骆驼股份": "骆驼集团股份有限公司",
        "桐昆股份": "桐昆集团股份有限公司",
        "广汽集团": "广州汽车集团股份有限公司",
        "庞大集团": "庞大汽贸集团股份有限公司",
        "杭齿前进": "杭州前进齿轮箱集团股份有限公司",
        "深圳燃气": "深圳市燃气集团股份有限公司",
        "小康股份": "重庆小康工业集团股份有限公司",
        "四方股份": "北京四方继保自动化股份有限公司",
        "海南橡胶": "海南天然橡胶产业集团股份有限公司",
        "华鼎股份": "义乌华鼎锦纶股份有限公司",
        "中国国航": "中国国际航空股份有限公司",
        "中南传媒": "中南出版传媒集团股份有限公司",
        "一拖股份": "第一拖拉机股份有限公司",
        "玉龙股份": "江苏玉龙钢管股份有限公司",
        "宁波港": "宁波舟山港股份有限公司",
        "节能风电": "中节能风力发电股份有限公司",
        "隆基股份": "隆基绿能科技股份有限公司",
        "文峰股份": "文峰大世界连锁发展股份有限公司",
        "柳钢股份": "柳州钢铁股份有限公司",
        "开滦股份": "开滦能源化工股份有限公司",
        "贵广网络": "贵州省广播电视信息网络股份有限公司",
        "汇鸿集团": "江苏汇鸿国际集团股份有限公司",
        "健民集团": "健民药业集团股份有限公司",
        "宝胜股份": "宝胜科技创新股份有限公司",
        "福成股份": "河北福成五丰食品股份有限公司",
        "株冶集团": "株洲冶炼集团股份有限公司",
        "江苏有线": "江苏省广电有线信息网络股份有限公司",
        "无锡银行": "无锡农村商业银行股份有限公司",
        "厦门空港": "元翔（厦门）国际航空港股份有限公司",
        "览海投资": "览海医疗产业投资股份有限公司",
        "大晟文化": "大晟时代文化投资股份有限公司",
        "中房股份": "中房置业股份有限公司",
        "中航动力": "中国航发动力股份有限公司",
        "伊利股份": "内蒙古伊利实业集团股份有限公司",
        "宏发股份": "宏发科技股份有限公司",
        "广泽股份": "上海广泽食品科技股份有限公司",
        "亚泰集团": "吉林亚泰(集团)股份有限公司",
        "航天电子": "航天时代电子技术股份有限公司",
        "中航高科": "中航航空高科技股份有限公司",
        "石化油服": "中石化石油工程技术服务股份有限公司",
        "厦华电子": "厦门华侨电子股份有限公司",
        "内蒙华电": "内蒙古蒙电华能热电股份有限公司",
        "京城股份": "北京京城机电股份有限公司",
        "春兰股份": "江苏春兰制冷设备股份有限公司",
        "银座股份": "银座集团股份有限公司",
        "龙建股份": "龙建路桥股份有限公司",
        "万里股份": "重庆万里新能源股份有限公司",
        "益民集团": "上海益民商业集团股份有限公司",
        "隧道股份": "上海隧道工程股份有限公司",
        "厦工股份": "厦门厦工机械股份有限公司",
        "神马股份": "神马实业股份有限公司",
        "山西汾酒": "山西杏花村汾酒厂股份有限公司",
        "马钢股份": "马鞍山钢铁股份有限公司",
        "天业股份": "山东天业恒基股份有限公司",
        "新奥股份": "新奥生态控股股份有限公司",
        "云煤能源": "云南煤业能源股份有限公司",
        "中储股份": "中储发展股份有限公司",
        "鲁信创投": "鲁信创业投资集团股份有限公司",
        "友好集团": "新疆友好(集团)股份有限公司",
        "新钢股份": "新余钢铁股份有限公司",
        "西藏城投": "西藏城市发展投资股份有限公司",
        "长江传媒": "长江出版传媒股份有限公司",
        "上实发展": "上海实业发展股份有限公司",
        "大连控股": "大连大福控股股份有限公司",
        "中粮糖业": "中粮屯河糖业股份有限公司",
        "苏州高新": "苏州新区高新技术产业股份有限公司",
        "佳都科技": "佳都新太科技股份有限公司",
        "首商股份": "北京首商集团股份有限公司",
        "凤凰股份": "江苏凤凰置业投资股份有限公司",
        "曲江文旅": "西安曲江文化旅游股份有限公司",
        "光明地产": "光明房地产集团股份有限公司",
        "彩虹股份": "彩虹显示器件股份有限公司",
        "上海石化": "中国石化上海石油化工股份有限公司",
        "中船防务": "中船海洋与防务装备股份有限公司",
        "南京新百": "南京新街口百货商店股份有限公司",
        "交运股份": "上海交运集团股份有限公司",
        "天目药业": "杭州天目山药业股份有限公司",
        "哈药股份": "哈药集团股份有限公司",
        "豫园商城": "上海豫园旅游商城股份有限公司",
        "浙数文化": "浙报数字文化集团股份有限公司",
        "龙头股份": "上海龙头(集团)股份有限公司",
        "华建集团": "华东建筑集团股份有限公司",
        "嘉宝集团": "上海嘉宝实业(集团)股份有限公司",
        "丰华股份": "上海丰华(集团)股份有限公司",
        "上海科技": "上海宽频科技股份有限公司",
        "新安股份": "浙江新安化工集团股份有限公司",
        "龙溪股份": "福建龙溪轴承(集团)股份有限公司",
        "海油工程": "海洋石油工程股份有限公司",
        "精达股份": "铜陵精达特种电磁线股份有限公司",
        "迪马股份": "重庆市迪马实业股份有限公司",
        "深高速": "深圳高速公路股份有限公司",
        "莫高股份": "甘肃莫高实业发展股份有限公司",
        "狮头股份": "太原狮头水泥股份有限公司",
        "新赛股份": "新疆赛里木现代农业股份有限公司",
        "国发股份": "北海国发海洋生物产业股份有限公司",
        "中铁工业": "中铁高新工业股份有限公司",
        "中发科技": "铜陵中发三佳科技股份有限公司",
        "贵航股份": "贵州贵航汽车零部件股份有限公司",
        "国药股份": "国药集团药业股份有限公司",
        "鹏欣资源": "鹏欣环球资源股份有限公司",
        "天药股份": "天津天药药业股份有限公司",
        "凌云股份": "凌云工业股份有限公司",
        "华光股份": "无锡华光锅炉股份有限公司",
        "百利电气": "天津百利特精电气股份有限公司",
        "空港股份": "北京空港科技园区股份有限公司",
        "风神股份": "风神轮胎股份有限公司",
        "博通股份": "西安博通资讯股份有限公司",
        "宝钛股份": "宝鸡钛业股份有限公司",
        "金证股份": "深圳市金证科技股份有限公司",
        "三元股份": "北京三元食品股份有限公司",
        "中远海特": "中远海运特种运输股份有限公司",
        "湘电股份": "湘潭电机股份有限公司",
        "红豆股份": "江苏红豆实业股份有限公司",
        "抚顺特钢": "抚顺特殊钢股份有限公司",
        "江山股份": "南通江山农药化工股份有限公司",
        "金地集团": "金地(集团)股份有限公司",
        "北巴传媒": "北京巴士传媒股份有限公司",
        "宝光股份": "陕西宝光真空电器股份有限公司",
        "天科股份": "四川天一科技股份有限公司",
        "首开股份": "北京首都开发股份有限公司",
        "中文传媒": "中文天地出版传媒股份有限公司",
        "中航电子": "中航航空电子系统股份有限公司",
        "通葡股份": "通化葡萄酒股份有限公司",
        "华联综超": "北京华联综合超市股份有限公司",
        "新农开发": "新疆塔里木农业综合开发股份有限公司",
        "旭光股份": "成都旭光电子股份有限公司",
        "恒力股份": "恒力石化股份有限公司",
        "中油工程": "中国石油集团工程股份有限公司",
        "美克家居": "美克国际家居用品股份有限公司",
        "天通股份": "天通控股股份有限公司",
        "华发股份": "珠海华发实业股份有限公司",
        "华泰股份": "山东华泰纸业股份有限公司",
        "天房发展": "天津市房地产发展(集团)股份有限公司",
        "酒钢宏兴": "甘肃酒钢集团宏兴钢铁股份有限公司",
        "曙光股份": "辽宁曙光汽车集团股份有限公司",
        "标准股份": "西安标准工业股份有限公司",
        "南化股份": "南宁化工股份有限公司",
        "维维股份": "维维食品饮料股份有限公司",
        "三峡新材": "湖北三峡新型建材股份有限公司",
        "西水股份": "内蒙古西水创业股份有限公司",
        "大恒科技": "大恒新纪元科技股份有限公司",
        "南钢股份": "南京钢铁股份有限公司",
        "太化股份": "太原化工股份有限公司",
        "东方创业": "东方国际创业股份有限公司",
        "外运发展": "中外运空运发展股份有限公司",
        "国电南自": "国电南京自动化股份有限公司",
        "北方股份": "内蒙古北方重型汽车股份有限公司",
        "大湖股份": "大湖水殖股份有限公司",
        "鑫科材料": "安徽鑫科新材料股份有限公司",
        "南纺股份": "南京纺织品进出口股份有限公司",
        "延长化建": "陕西延长石油化建股份有限公司",
        "冠农股份": "新疆冠农果茸集团股份有限公司",
        "成城股份": "吉林成城集团股份有限公司",
        "民丰特纸": "民丰特种纸股份有限公司",
        "凌钢股份": "凌源钢铁股份有限公司",
        "昌九生化": "江西昌九生物化工股份有限公司",
        "中再资环": "中再资源环境股份有限公司",
        "西藏药业": "西藏诺迪康药业股份有限公司",
        "哈空调": "哈尔滨空调股份有限公司",
        "生物股份": "金宇生物技术股份有限公司",
        "精工钢构": "长江精工钢结构(集团)股份有限公司",
        "中牧股份": "中牧实业股份有限公司",
        "吉林森工": "吉林森林工业股份有限公司",
        "东安动力": "哈尔滨东安汽车动力股份有限公司",
        "大龙地产": "北京市大龙伟业房地产开发股份有限公司",
        "航天机电": "上海航天汽车机电股份有限公司",
        "新亿股份": "新疆亿路万源实业投资控股股份有限公司",
        "兴发集团": "湖北兴发化工集团股份有限公司",
        "浪莎股份": "四川浪莎控股股份有限公司",
        "太极集团": "重庆太极实业(集团)股份有限公司",
        "杭钢股份": "杭州钢铁股份有限公司",
        "铁龙物流": "中铁铁龙集装箱物流股份有限公司",
        "兰花科创": "山西兰花科技创业股份有限公司",
        "中国卫星": "中国东方红卫星股份有限公司",
        "西宁特钢": "西宁特殊钢股份有限公司",
        "诺德股份": "诺德投资股份有限公司",
        "东睦股份": "东睦新材料集团股份有限公司",
        "亚盛集团": "甘肃亚盛实业(集团)股份有限公司",
        "上汽集团": "上海汽车集团股份有限公司",
        "中葡股份": "中信国安葡萄酒业股份有限公司",
        "金花股份": "金花企业(集团)股份有限公司",
        "博信股份": "广东博信投资控股股份有限公司",
        "海泰发展": "天津海泰科技发展股份有限公司",
        "东风科技": "东风电子科技股份有限公司",
        "澄星股份": "江苏澄星磷化工股份有限公司",
        "宋都股份": "宋都基业投资股份有限公司",
        "银鸽投资": "河南银鸽实业投资股份有限公司",
        "中国联通": "中国联合网络通信股份有限公司",
        "中直股份": "中航直升机股份有限公司",
        "保利地产": "保利房地产(集团)股份有限公司",
        "福建高速": "福建发展高速公路股份有限公司",
        "中国石化": "中国石油化工股份有限公司",
        "中远海能": "中远海运能源运输股份有限公司",
        "上海机场": "上海国际机场股份有限公司",
        "中国国贸": "中国国际贸易中心股份有限公司",
        "包钢股份": "内蒙古包钢钢联股份有限公司",
        "白云机场": "广州白云国际机场股份有限公司",
        "浦发银行": "上海浦东发展银行股份有限公司",
        "太龙照明": "太龙（福建）商业照明股份有限公司",
        "星云股份": "福建星云电子股份有限公司",
        "正丹股份": "江苏正丹化学工业股份有限公司",
        "德艺文创": "德艺文化创意集团股份有限公司",
        "光莆股份": "厦门光莆电子股份有限公司",
        "达安股份": "广东达安项目管理股份有限公司",
        "开立医疗": "深圳开立生物医疗科技股份有限公司",
        "华瑞股份": "华瑞电器股份有限公司",
        "维业股份": "深圳市维业装饰集团股份有限公司",
        "安靠智电": "江苏安靠智能输电工程科技股份有限公司",
        "汇纳科技": "上海汇纳信息科技股份有限公司",
        "晨化股份": "扬州晨化新材料股份有限公司",
        "瑞特股份": "常熟瑞特电气股份有限公司",
        "奥联电子": "南京奥联汽车电子电器股份有限公司",
        "天铁股份": "浙江天铁实业股份有限公司",
        "中旗股份": "江苏中旗作物保护股份有限公司",
        "科信技术": "深圳市科信通信技术股份有限公司",
        "神宇股份": "神宇通信科技股份公司",
        "古鳌科技": "上海古鳌电子科技股份有限公司",
        "集智股份": "杭州集智机电股份有限公司",
        "联得装备": "深圳市联得自动化装备股份有限公司",
        "深冷股份": "成都深冷液化设备股份有限公司",
        "广信材料": "江苏广信感光新材料股份有限公司",
        "同益股份": "深圳市同益实业股份有限公司",
        "达威股份": "四川达威科技股份有限公司",
        "达志科技": "广东达志环保科技股份有限公司",
        "海波重科": "海波重型工程科技股份有限公司",
        "中亚股份": "杭州中亚机械股份有限公司",
        "维宏股份": "上海维宏电子科技股份有限公司",
        "苏奥传感": "江苏奥力威传感高科股份有限公司",
        "高澜股份": "广州高澜节能技术股份有限公司",
        "温氏股份": "广东温氏食品集团股份有限公司",
        "富祥股份": "江西富祥药业股份有限公司",
        "通合科技": "石家庄通合电子科技股份有限公司",
        "中飞股份": "哈尔滨中飞新技术股份有限公司",
        "沃施股份": "上海沃施园艺股份有限公司",
        "聚隆科技": "安徽聚隆传动科技股份有限公司",
        "德尔股份": "阜新德尔汽车部件股份有限公司",
        "厚普股份": "成都华气厚普机电设备股份有限公司",
        "迅游科技": "四川迅游网络科技股份有限公司",
        "山河药辅": "安徽山河药用辅料股份有限公司",
        "全信股份": "南京全信传输科技股份有限公司",
        "鲍斯股份": "宁波鲍斯能源装备股份有限公司",
        "中泰股份": "杭州中泰深冷技术股份有限公司",
        "四通新材": "河北四通新型金属材料股份有限公司",
        "强力新材": "常州强力电子新材料股份有限公司",
        "航新科技": "广州航新航空科技股份有限公司",
        "力星股份": "江苏力星通用钢球股份有限公司",
        "浩丰科技": "北京浩丰创源科技股份有限公司",
        "金盾股份": "浙江金盾风机股份有限公司",
        "三环集团": "潮州三环(集团)股份有限公司",
        "科隆精化": "辽宁科隆精细化工股份有限公司",
        "天孚通信": "苏州天孚光通信股份有限公司",
        "中来股份": "苏州中来光伏新材股份有限公司",
        "腾信股份": "北京腾信创新网络营销技术股份有限公司",
        "富邦股份": "湖北富邦科技股份有限公司",
        "恒通科技": "北京恒通创新赛木科技股份有限公司",
        "扬杰科技": "扬州扬杰电子科技股份有限公司",
        "汇中股份": "汇中仪表股份有限公司",
        "恒华科技": "北京恒华伟业科技股份有限公司",
        "绿盟科技": "北京神州绿盟信息安全科技股份有限公司",
        "汇金股份": "河北汇金机电股份有限公司",
        "博腾股份": "重庆博腾制药科技股份有限公司",
        "红宇新材": "湖南红宇耐磨新材料股份有限公司",
        "津膜科技": "天津膜天膜科技股份有限公司",
        "麦迪电气": "麦克奥迪(厦门)电气股份有限公司",
        "同大股份": "山东同大海岛新材料股份有限公司",
        "海达股份": "江阴海达橡塑股份有限公司",
        "麦捷科技": "深圳市麦捷微电子科技股份有限公司",
        "珈伟股份": "深圳珈伟光伏照明股份有限公司",
        "天山生物": "新疆天山畜牧生物工程股份有限公司",
        "中际装备": "山东中际电工装备股份有限公司",
        "同有科技": "北京同有飞骥科技股份有限公司",
        "裕兴股份": "江苏裕兴薄膜科技股份有限公司",
        "富春股份": "富春科技股份有限公司",
        "蓝盾股份": "蓝盾信息安全技术股份有限公司",
        "蓝英装备": "沈阳蓝英工业自动化装备股份有限公司",
        "国瓷材料": "山东国瓷功能材料股份有限公司",
        "汇冠股份": "北京汇冠新技术股份有限公司",
        "海顺新材": "上海海顺新型药用包装材料股份有限公司",
        "和佳股份": "珠海和佳医疗设备股份有限公司",
        "通光线缆": "江苏通光电子线缆股份有限公司",
        "隆华节能": "洛阳隆华传热节能股份有限公司",
        "新莱应材": "昆山新莱洁净应用材料股份有限公司",
        "开山股份": "浙江开山压缩机股份有限公司",
        "常山药业": "河北常山生化药业股份有限公司",
        "瑞丰高材": "山东瑞丰高分子材料股份有限公司",
        "银信科技": "北京银信长远科技股份有限公司",
        "永利股份": "上海永利带业股份有限公司",
        "富瑞特装": "张家港富瑞特种装备股份有限公司",
        "正海磁材": "烟台正海磁性材料股份有限公司",
        "安利股份": "安徽安利材料科技股份有限公司",
        "千山药机": "湖南千山制药机械股份有限公司",
        "电科院": "苏州电器科学研究院股份有限公司",
        "亿通科技": "江苏亿通高科技股份有限公司",
        "森远股份": "鞍山森远路桥股份有限公司",
        "长海股份": "江苏长海复合材料股份有限公司",
        "纳川股份": "福建纳川管材科技股份有限公司",
        "长荣股份": "天津长荣印刷设备股份有限公司",
        "捷成股份": "北京捷成世纪科技股份有限公司",
        "智慧松德": "松德智慧装备股份有限公司",
        "新研股份": "新疆机械研究院股份有限公司",
        "秀强股份": "江苏秀强玻璃工艺股份有限公司",
        "雷曼股份": "深圳雷曼光电科技股份有限公司",
        "瑞凌股份": "深圳市瑞凌实业股份有限公司",
        "英唐智控": "深圳市英唐智能控制股份有限公司",
        "锐奇股份": "锐奇控股股份有限公司",
        "嘉寓股份": "北京嘉寓门窗幕墙股份有限公司",
        "建新股份": "河北建新化工股份有限公司",
        "双龙股份": "通化双龙化工股份有限公司",
        "龙源技术": "烟台龙源电力技术股份有限公司",
        "达刚路机": "西安达刚路面机械股份有限公司",
        "双林股份": "宁波双林汽车部件股份有限公司",
        "智云股份": "大连智云自动化装备股份有限公司",
        "华伍股份": "江西华伍制动器股份有限公司",
        "华平股份": "华平信息技术股份有限公司",
        "当升科技": "北京当升材料科技股份有限公司",
        "豫金刚石": "郑州华晶金刚石股份有限公司",
        "天龙集团": "广东天龙油墨集团股份有限公司",
        "万顺股份": "汕头万顺包装材料股份有限公司",
        "鼎龙股份": "湖北鼎龙控股股份有限公司",
        "福瑞股份": "内蒙古福瑞医疗科技股份有限公司",
        "台基股份": "湖北台基半导体股份有限公司",
        "星辉娱乐": "星辉互动娱乐股份有限公司",
        "宝德股份": "西安宝德自动化股份有限公司",
        "中元股份": "武汉中元华电科技股份有限公司",
        "天海防务": "天海融合防务装备技术股份有限公司",
        "乐普医疗": "乐普(北京)医疗器械股份有限公司",
        "南风股份": "南方风机股份有限公司",
        "美芝股份": "深圳市美芝装饰设计工程股份有限公司",
        "视源股份": "广州视源电子科技股份有限公司",
        "华统股份": "浙江华统肉制品股份有限公司",
        "张家港行": "江苏张家港农村商业银行股份有限公司",
        "洁美科技": "浙江洁美电子科技股份有限公司",
        "道恩股份": "山东道恩高分子材料股份有限公司",
        "同为股份": "深圳市同为数码科技股份有限公司",
        "裕同科技": "深圳市裕同包装科技股份有限公司",
        "名雕股份": "深圳市名雕装饰股份有限公司",
        "易明医药": "西藏易明西雅医药科技股份有限公司",
        "纳尔股份": "上海纳尔数码喷印材料股份有限公司",
        "和胜股份": "广东和胜工业铝材股份有限公司",
        "创新股份": "云南创新新材料股份有限公司",
        "崇达技术": "深圳市崇达电路技术股份有限公司",
        "江阴银行": "江苏江阴农村商业银行股份有限公司",
        "华锋股份": "肇庆华锋电子铝箔股份有限公司",
        "丰元股份": "山东丰元化学股份有限公司",
        "微光股份": "杭州微光电子股份有限公司",
        "吉宏股份": "厦门吉宏包装科技股份有限公司",
        "天顺股份": "新疆天顺供应链股份有限公司",
        "东音股份": "浙江东音泵业股份有限公司",
        "建艺集团": "深圳市建艺装饰集团股份有限公司",
        "凯龙股份": "湖北凯龙化工集团股份有限公司",
        "永和智控": "永和流体智控股份有限公司",
        "奇信股份": "深圳市奇信建设集团股份有限公司",
        "国恩股份": "青岛国恩科技股份有限公司",
        "索菱股份": "深圳市索菱实业股份有限公司",
        "蓝黛传动": "重庆蓝黛动力传动机械股份有限公司",
        "汇洁股份": "深圳汇洁集团股份有限公司",
        "凤形股份": "安徽省凤形耐磨材料股份有限公司",
        "天际股份": "广东天际电器股份有限公司",
        "永东股份": "山西永东化工股份有限公司",
        "永兴特钢": "永兴特种不锈钢股份有限公司",
        "昇兴股份": "昇兴集团股份有限公司",
        "国光股份": "四川国光农化股份有限公司",
        "万达院线": "万达电影院线股份有限公司",
        "萃华珠宝": "沈阳萃华金银珠宝股份有限公司",
        "利民股份": "利民化工股份有限公司",
        "雄韬股份": "深圳市雄韬电源科技股份有限公司",
        "电光科技": "电光防爆科技股份有限公司",
        "金轮股份": "金轮蓝海股份有限公司",
        "友邦吊顶": "浙江友邦集成吊顶股份有限公司",
        "登云股份": "怀集登云汽配股份有限公司",
        "牧原股份": "牧原食品股份有限公司",
        "新宝股份": "广东新宝电器股份有限公司",
        "博实股份": "哈尔滨博实自动化股份有限公司",
        "百洋股份": "百洋产业投资集团股份有限公司",
        "冀凯股份": "冀凯装备制造股份有限公司",
        "睿康股份": "睿康文远电缆股份有限公司",
        "华东重机": "无锡华东重型机械股份有限公司",
        "猛狮科技": "广东猛狮新能源科技股份有限公司",
        "龙洲股份": "福建龙洲运输股份有限公司",
        "兴业科技": "兴业皮革科技股份有限公司",
        "龙泉股份": "山东龙泉管道工程股份有限公司",
        "鞍重股份": "鞍山重型矿山机器股份有限公司",
        "首航节能": "北京首航艾启威节能技术股份有限公司",
        "康达新材": "上海康达化工新材料股份有限公司",
        "普邦股份": "广州普邦园林股份有限公司",
        "京威股份": "北京威卡威汽车零部件股份有限公司",
        "扬子新材": "苏州扬子江新型材料股份有限公司",
        "利君股份": "成都利君实业股份有限公司",
        "申科股份": "申科滑动轴承股份有限公司",
        "勤上股份": "东莞勤上光电股份有限公司",
        "棒杰股份": "浙江棒杰数码针织品股份有限公司",
        "成都路桥": "成都市路桥工程股份有限公司",
        "龙生股份": "浙江龙生汽车部件股份有限公司",
        "三垒股份": "大连三垒机器股份有限公司",
        "长青集团": "广东长青(集团)股份有限公司",
        "瑞和股份": "深圳瑞和建筑装饰股份有限公司",
        "北玻股份": "洛阳北方玻璃技术股份有限公司",
        "围海股份": "浙江省围海建设集团股份有限公司",
        "双星新材": "江苏双星彩塑新材料股份有限公司",
        "未名医药": "山东未名生物医药股份有限公司",
        "圣阳股份": "山东圣阳电源股份有限公司",
        "德力股份": "安徽德力日用玻璃股份有限公司",
        "步森股份": "浙江步森服饰股份有限公司",
        "顺灏股份": "上海顺灏新材料科技股份有限公司",
        "通达股份": "河南通达电缆股份有限公司",
        "亚威股份": "江苏亚威机床股份有限公司",
        "辉隆股份": "安徽辉隆农资集团股份有限公司",
        "千红制药": "常州千红生化制药股份有限公司",
        "万和电气": "广东万和新电气股份有限公司",
        "西泵股份": "河南省西峡汽车水泵股份有限公司",
        "鸿路钢构": "安徽鸿路钢结构(集团)股份有限公司",
        "亚太科技": "江苏亚太轻合金科技股份有限公司",
        "杭锅股份": "杭州锅炉集团股份有限公司",
        "海源机械": "福建海源自动化机械股份有限公司",
        "丰东股份": "江苏丰东热技术股份有限公司",
        "日发精机": "浙江日发精密机械股份有限公司",
        "蓝丰生化": "江苏蓝丰生物化工股份有限公司",
        "天汽模": "天津汽车模具股份有限公司",
        "大康农业": "湖南大康国际农业食品股份有限公司",
        "佳隆股份": "广东佳隆食品股份有限公司",
        "华斯股份": "华斯控股股份有限公司",
        "江海股份": "南通江海电容器股份有限公司",
        "润邦股份": "江苏润邦重工股份有限公司",
        "新筑股份": "成都市新筑路桥机械股份有限公司",
        "富春环保": "浙江富春江环保热电股份有限公司",
        "常宝股份": "江苏常宝钢管股份有限公司",
        "宝莫股份": "山东宝莫生物化工股份有限公司",
        "三维工程": "山东三维石化工程股份有限公司",
        "金利科技": "昆山金利表面材料应用科技股份有限公司",
        "益生股份": "山东益生种畜禽股份有限公司",
        "沪电股份": "沪士电子股份有限公司",
        "百川股份": "无锡百川化工股份有限公司",
        "松芝股份": "上海加冷松芝汽车空调股份有限公司",
        "天马精化": "苏州天马精细化学品股份有限公司",
        "壹桥股份": "大连壹桥海参股份有限公司",
        "中南文化": "中南红文化集团股份有限公司",
        "长高集团": "湖南长高高压开关集团股份公司",
        "棕榈股份": "棕榈生态城镇发展股份有限公司",
        "尤夫股份": "浙江尤夫高新纤维股份有限公司",
        "云南锗业": "云南临沧鑫圆锗业股份有限公司",
        "凯撒文化": "凯撒(中国)文化股份有限公司",
        "毅昌股份": "广州毅昌科技股份有限公司",
        "天虹股份": "天虹商场股份有限公司",
        "必康股份": "江苏必康制药股份有限公司",
        "中海科技": "中海网络科技股份有限公司",
        "省广股份": "广东省广告集团股份有限公司",
        "建研集团": "厦门市建筑科学研究院集团股份有限公司",
        "梦洁股份": "湖南梦洁家纺股份有限公司",
        "联发股份": "江苏联发纺织股份有限公司",
        "长青股份": "江苏长青农化股份有限公司",
        "新亚制程": "深圳市新亚电子制程股份有限公司",
        "双象股份": "无锡双象超纤材料股份有限公司",
        "双箭股份": "浙江双箭橡胶股份有限公司",
        "科远股份": "南京科远自动化集团股份有限公司",
        "伟星新材": "浙江伟星新型建材股份有限公司",
        "亚厦股份": "浙江亚厦装饰股份有限公司",
        "太极股份": "太极计算机股份有限公司",
        "台海核电": "台海玛努尔核电设备股份有限公司",
        "神剑股份": "安徽神剑新材料股份有限公司",
        "杰瑞股份": "烟台杰瑞石油服务集团股份有限公司",
        "柘中股份": "上海柘中集团股份有限公司",
        "海宁皮城": "海宁中国皮革城股份有限公司",
        "新朋股份": "上海新朋实业股份有限公司",
        "洪涛股份": "深圳市洪涛装饰股份有限公司",
        "海峡股份": "海南海峡航运股份有限公司",
        "理工环科": "宁波理工环境能源科技股份有限公司",
        "乐通股份": "珠海市乐通化工股份有限公司",
        "威创股份": "威创集团股份有限公司",
        "洋河股份": "江苏洋河酒厂股份有限公司",
        "中电鑫龙": "安徽中电兴发与鑫龙科技股份有限公司",
        "中科新材": "苏州中科创新型材料股份有限公司",
        "精艺股份": "广东精艺金属股份有限公司",
        "亚太股份": "浙江亚太机电股份有限公司",
        "神开股份": "上海神开石油化工装备股份有限公司",
        "友阿股份": "湖南友谊阿波罗商业股份有限公司",
        "华明装备": "华明电力装备股份有限公司",
        "美邦服饰": "上海美特斯邦威服饰股份有限公司",
        "陕天然气": "陕西省天然气股份有限公司",
        "西仪股份": "云南西仪工业股份有限公司",
        "德奥通航": "德奥通用航空股份有限公司",
        "兆新股份": "深圳市兆新能源股份有限公司",
        "北化股份": "四川北方硝化棉股份有限公司",
        "滨江集团": "杭州滨江房产集团股份有限公司",
        "恒邦股份": "山东恒邦冶炼股份有限公司",
        "大华股份": "浙江大华技术股份有限公司",
        "民和股份": "山东民和牧业股份有限公司",
        "濮耐股份": "濮阳濮耐高温材料(集团)股份有限公司",
        "南洋股份": "广东南洋电缆集团股份有限公司",
        "准油股份": "新疆准东石油技术股份有限公司",
        "国统股份": "新疆国统管道股份有限公司",
        "大连重工": "大连华锐重工集团股份有限公司",
        "山东如意": "山东济宁如意毛纺织股份有限公司",
        "云海金属": "南京云海特种金属股份有限公司",
        "粤传媒": "广东广州日报传媒股份有限公司",
        "御银股份": "广州御银科技股份有限公司",
        "江特电机": "江西特种电机股份有限公司",
        "东方网络": "东方时代网络传媒股份有限公司",
        "楚江新材": "安徽楚江科技新材料股份有限公司",
        "芭田股份": "深圳市芭田生态工程股份有限公司",
        "深圳惠程": "深圳市惠程电气股份有限公司",
        "西部材料": "西部金属材料股份有限公司",
        "荣盛发展": "荣盛房地产发展股份有限公司",
        "中核钛白": "中核华原钛白股份有限公司",
        "印纪传媒": "印纪娱乐传媒股份有限公司",
        "东华科技": "东华工程科技股份有限公司",
        "利欧股份": "利欧集团股份有限公司",
        "银轮股份": "浙江银轮机械股份有限公司",
        "天马股份": "天马轴承集团股份有限公司",
        "韵达股份": "韵达控股股份有限公司",
        "天润数娱": "湖南天润数字娱乐文化传媒股份有限公司",
        "兴化股份": "陕西兴化化学股份有限公司",
        "广博股份": "广博集团股份有限公司",
        "冠福股份": "冠福控股股份有限公司",
        "浔兴股份": "福建浔兴拉链科技股份有限公司",
        "孚日股份": "孚日集团股份有限公司",
        "南岭民爆": "湖南南岭民用爆破器材股份有限公司",
        "黑猫股份": "江西黑猫炭黑股份有限公司",
        "横店东磁": "横店集团东磁股份有限公司",
        "中钢天源": "中钢集团安徽天源科技股份有限公司",
        "德美化工": "广东德美精细化工集团股份有限公司",
        "云南能投": "云南能源投资股份有限公司",
        "宝鹰股份": "深圳市宝鹰建设控股集团股份有限公司",
        "美年健康": "美年大健康产业控股股份有限公司",
        "久联发展": "贵州久联民爆器材发展股份有限公司",
        "丽江旅游": "丽江玉龙旅游股份有限公司",
        "中环股份": "天津中环半导体股份有限公司",
        "中航机电": "中航工业机电系统股份有限公司",
        "凯恩股份": "浙江凯恩特种材料股份有限公司",
        "盾安环境": "浙江盾安人工环境股份有限公司",
        "天奇股份": "天奇自动化工程股份有限公司",
        "伟星股份": "浙江伟星实业发展股份有限公司",
        "华邦健康": "华邦生命健康股份有限公司",
        "中鲁股份": "山东省中鲁远洋渔业股份有限公司",
        "粤华包": "佛山华新包装股份有限公司",
        "瓦轴": "瓦房店轴承股份有限公司",
        "苏常柴": "常柴股份有限公司",
        "佛山照明": "佛山电器照明股份有限公司",
        "粤电力": "广东电力发展股份有限公司",
        "大冷股份": "大连冷冻机股份有限公司",
        "闽灿坤": "厦门灿坤实业股份有限公司",
        "美菱电器": "合肥美菱股份有限公司",
        "宁通信": "南京普天通信股份有限公司",
        "粤高速": "广东省高速公路发展股份有限公司",
        "山航": "山东航空股份有限公司",
        "深赛格": "深圳赛格股份有限公司",
        "三花智控": "浙江三花智能控制股份有限公司",
        "深基地": "深圳赤湾石油基地股份有限公司",
        "建摩": "重庆建设摩托车股份有限公司",
        "深康佳": "康佳集团股份有限公司",
        "深中华": "深圳中华自行车(集团)股份有限公司",
        "招商蛇口": "招商局蛇口工业区控股股份有限公司",
        "深物业": "深圳市物业发展(集团)股份有限公司",
        "隆平高科": "袁隆平农业高科技股份有限公司",
        "银亿股份": "银亿房地产股份有限公司",
        "中弘股份": "中弘控股股份有限公司",
        "越秀金控": "广州越秀金融控股集团股份有限公司",
        "浪潮信息": "浪潮电子信息产业股份有限公司",
        "华西股份": "江苏华西村股份有限公司",
        "中粮生化": "中粮生物化学(安徽)股份有限公司",
        "福星股份": "湖北福星科技股份有限公司",
        "河北宣工": "河北宣化工程机械股份有限公司",
        "佳电股份": "哈尔滨电气集团佳木斯电机股份有限公司",
        "双汇发展": "河南双汇投资发展股份有限公司",
        "华联股份": "北京华联商厦股份有限公司",
        "中广核技": "中广核核技术发展股份有限公司",
        "天山股份": "新疆天山水泥股份有限公司",
        "安凯客车": "安徽安凯汽车股份有限公司",
        "吉电股份": "吉林电力股份有限公司",
        "海印股份": "广东海印集团股份有限公司",
        "石化机械": "中石化石油机械股份有限公司",
        "高鸿股份": "大唐高鸿数据网络技术股份有限公司",
        "华茂股份": "安徽华茂纺织股份有限公司",
        "财信发展": "财信国兴地产发展股份有限公司",
        "长城动漫": "长城国际动漫游戏股份有限公司",
        "贵糖股份": "广西贵糖(集团)股份有限公司",
        "天音控股": "天音通信控股股份有限公司",
        "东莞控股": "东莞发展控股股份有限公司",
        "德展健康": "德展大健康股份有限公司",
        "金宇车城": "四川金宇汽车城(集团)股份有限公司",
        "云铝股份": "云南铝业股份有限公司",
        "北京文化": "北京京西文化旅游股份有限公司",
        "中水渔业": "中水集团远洋股份有限公司",
        "盐湖股份": "青海盐湖工业股份有限公司",
        "北新建材": "北新集团建材股份有限公司",
        "中核科技": "中核苏阀科技实业股份有限公司",
        "美达股份": "广东新会美达锦纶股份有限公司",
        "中百集团": "中百控股集团股份有限公司",
        "中色股份": "中国有色金属建设股份有限公司",
        "浩物股份": "四川浩物机电股份有限公司",
        "西藏发展": "西藏银河科技发展股份有限公司",
        "航发控制": "中国航发动力控制股份有限公司",
        "振华科技": "中国振华(集团)科技股份有限公司",
        "华东科技": "南京华东电子信息科技股份有限公司",
        "中兴商业": "中兴-沈阳商业大厦(集团)股份有限公司",
        "锦龙股份": "广东锦龙发展股份有限公司",
        "大冶特钢": "大冶特殊钢股份有限公司",
        "宝新能源": "广东宝丽华新能源股份有限公司",
        "山推股份": "山推工程机械股份有限公司",
        "襄阳轴承": "襄阳汽车轴承股份有限公司",
        "视觉中国": "视觉(中国)文化发展股份有限公司",
        "智度股份": "智度科技股份有限公司",
        "经纬纺机": "经纬纺织机械股份有限公司",
        "湖北广电": "湖北省广播电视信息网络股份有限公司",
        "金科股份": "金科地产集团股份有限公司",
        "万方发展": "万方城镇投资发展股份有限公司",
        "茂化实华": "茂名石化实华股份有限公司",
        "风华高科": "广东风华高新科技股份有限公司",
        "神火股份": "河南神火煤电股份有限公司",
        "攀钢钒钛": "攀钢集团钒钛资源股份有限公司",
        "天茂集团": "天茂实业集团股份有限公司",
        "远大控股": "远大产业控股股份有限公司",
        "中油资本": "中国石油集团资本股份有限公司",
        "京汉股份": "京汉实业投资股份有限公司",
        "阳光股份": "阳光新业地产股份有限公司",
        "天首发展": "内蒙古天首科技发展股份有限公司",
        "渤海股份": "渤海水业股份有限公司",
        "韶能股份": "广东韶能集团股份有限公司",
        "黔轮胎": "贵州轮胎股份有限公司",
        "友利控股": "江苏友利投资控股股份有限公司",
        "汇源通信": "四川汇源光通信股份有限公司",
        "广东甘化": "江门甘蔗化工厂(集团)股份有限公司",
        "粤宏远": "东莞宏远工业区股份有限公司",
        "海德股份": "海南海德实业股份有限公司",
        "渝三峡": "重庆三峡油漆股份有限公司",
        "陕国投": "陕西省国际信托股份有限公司",
        "昆百大": "昆明百货大楼(集团)股份有限公司",
        "莱茵体育": "莱茵达体育发展股份有限公司",
        "神州信息": "神州数码信息服务股份有限公司",
        "航天发展": "航天工业发展股份有限公司",
        "金圆股份": "金圆水泥股份有限公司",
        "皖能电力": "安徽省皖能股份有限公司",
        "万泽股份": "万泽实业股份有限公司",
        "穗恒运": "广州恒运企业集团股份有限公司",
        "岭南控股": "广州岭南集团控股股份有限公司",
        "广州浪奇": "广州市浪奇实业股份有限公司",
        "丽珠集团": "丽珠医药集团股份有限公司",
        "鄂武商": "武汉武商集团股份有限公司",
        "山东路桥": "山东高速路桥集团股份有限公司",
        "徐工机械": "徐工集团工程机械股份有限公司",
        "东方市场": "江苏吴江中国东方丝绸市场股份有限公司",
        "常山股份": "石家庄常山纺织股份有限公司",
        "中信海直": "中信海洋直升机股份有限公司",
        "中成股份": "中成进出口股份有限公司",
        "天健集团": "深圳市天健(集团)股份有限公司",
        "深圳机场": "深圳市机场股份有限公司",
        "华锦股份": "北方华锦化学工业股份有限公司",
        "深天马": "天马微电子股份有限公司",
        "中洲控股": "深圳市中洲投资控股股份有限公司",
        "中集集团": "中国国际海运集装箱(集团)股份有限公司",
        "深大通": "深圳大通实业股份有限公司",
        "沙河股份": "沙河实业股份有限公司",
        "深振业": "深圳市振业(集团)股份有限公司",
        "国农科技": "深圳中国农大科技股份有限公司",
        "海虹控股": "海虹企业(控股)股份有限公司"
    }
    result_dict = {}
    output_logger = generate_logger("CJOAbbrFullSpider")

    def start_requests(self):
        for abbr, full in self.abbr_full_dict.items():
            param = {}
            param["当事人"] = abbr
            param = self.join_param(param)
            yield self.yield_formrequest(param, 1)

            param = {}
            param["当事人"] = full
            param = self.join_param(param)
            yield self.yield_formrequest(param, 1)

    def yield_formrequest(self, param, index):
        data = {
            # "Param": "案件类型:刑事案件,法院层级:高级法院",
            "Param": param,
            "Index": repr(index),
            "Page": repr(self.cases_per_page),
            "Order": "法院层级",
            "Direction": "asc",
        }

        return scrapy.FormRequest(url=self.url, formdata=data, callback=lambda response: self.parse(response, data), dont_filter=True)   # 关闭URL去重(有些url请求不成功，需要重新yield。如果打开URL去重, 这些请求无法成功?)

    def parse(self, response, data):
        """
        先按序请求各个start_url， 然后才会进入到parse中(可能是异步处理的，当start_urls比较多时，可能先进入parse? 待确定, 内部实现细节和工作原理)
        """
        body = urllib.parse.unquote_plus(response.request.body.decode("utf-8"), encoding="utf-8")
        # body: "Param=裁判日期:2016-02-07 TO 2016-02-07,案件类型:刑事案件&Index=1&Page=20&Order=法院层级&Direction=asc"
        print("body:", body)
        print("data:", data)

        text = response.text
        try:
            text_str = json.loads(text)
            text_list = json.loads(text_str)  # I don't know why I need json.loads() twice. ??????

            total_count = int(text_list[0]["Count"])
            print("Count:", total_count)
            self.result_dict[data["Param"].split(":")[1]] = total_count
            print(self.result_dict)
            self.output_logger.debug(self.result_dict)
            # self.output_logger.flush()
        except json.JSONDecodeError as jde:
            if "<title>502</title>" in response.text:
                print("The website returns 502")
                time.sleep(10)  # 服务器压力大，休息会儿
            elif "remind" in response.text:
                print("Bad news: the website block the spider")
                time.sleep(10)  # IP代理被禁用了，休息会儿等会儿新的代理
            else:
                print("lxw_JSONDecodeError_NOTE:", jde)
            # 针对这些抓取不成功的case, 重新yield进行抓取
            yield scrapy.FormRequest(url=self.url, formdata=data, callback=lambda resp: self.parse(resp, data), dont_filter=True)
        except Exception as e:
            print("lxw_Exception_NOTE:", e)
            # 针对这些抓取不成功的case, 重新yield进行抓取
            # TODO: 增加记录哪些案例应该爬取，哪些案例爬取过了，哪些没有爬取
            # "lxw_Exception_NOTE: 'Logger' object has no attribute 'flush'", 实际上此时已经爬取成功了，不能重新yield，这种情况要求必须要提供记录哪些案例(data即可)爬取过了，哪些没有爬取，然后重爬没有爬取到的
            # yield scrapy.FormRequest(url=self.url, formdata=data, callback=lambda resp: self.parse(resp, data), dont_filter=True)
            self.output_logger.error("[NOTE: NOT CRAWLED]: " + json.dumps(data))

    def join_param(self, param):
        """
        :param param: type(param) dict
        :return: str
        """
        str_list = []
        for key, value in param.items():
            str_list.append("{0}:{1}".format(key, value))
        return ",".join(str_list)
