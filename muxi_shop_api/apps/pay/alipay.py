import base64
import json
from base64 import encodebytes
from datetime import datetime
from urllib.parse import quote_plus
from muxi_shop_api import settings
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256

class Alipay():
    def __init__(self):
        self.appid=settings.APPID
        self.app_notify_url=settings.APP_NOTIFY_URL
        self.return_url = settings.RETURN_URL
        self.debug = settings.ALIPAY_DEBUG
        self.app_private_key_path = settings.PRIVATE_KEY_PATH
        self.ali_pub_key_path = settings.ALI_PUB_KEY_PATH
        
        self.app_private_key=None
        self.ali_pub_key = None

        with open(self.app_private_key_path) as fp:
            self.app_private_key = RSA.importKey(fp.read())
        
        with open(self.ali_pub_key_path) as fp:
            self.ali_pub_key = RSA.importKey(fp.read())
        
        if self.debug is True:
            self.__gateway = "https://openapi.alipaydev.com/gateway.do"
        else:
            self.__gateway = "https://openapi.alipay.com/gateway.do"
    
    @property
    def gateway(self):
        return self.__gateway

    #解析必要参数
    def direct_pay(self,subject,out_trade_no,total_amount,**kwargs):
        biz_content = {
            "subject":subject,
            "out_trade_no":out_trade_no,
            "total_amount":str(total_amount),
            "product_code":"FAST_INSTANT_TRADE_PAY",
        }
        biz_content.update(kwargs)
        data = self.build_body("alipay.trade.page.pay",biz_content,self.return_url)
        return self.sign_data(data)
    
    #构建公共请求参数
    def build_body(self,method,biz_content,return_url=None):
        data = {
            "app_id":self.appid,
            "method":method,
            "charset":"utf-8",
            "sign_type":"RSA2",
            "timestamp":datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "version":"1.0",
            "biz_content":biz_content
        }

        if return_url is not None:
            data["notify_url"] = self.app_notify_url
            data["return_url"] = self.return_url
    
        return data
    
    #数据签名逻辑
    def sign_data(self,data):
        data.pop("sign",None)
        #排序后的字符串
        unsigned_items = self.order_data(data)
        ugsigned_string = "&".join("{0}={1}".format(k,v) for k,v in unsigned_items)
        key = self.app_private_key
        signer = PKCS1_v1_5.new(key)
        signature = signer.sign(SHA256.new(ugsigned_string.encode("utf-8")))
        #base64编码 转换为unicode表示并移除回车
        sign = encodebytes(signature).decode("utf8").replace('\n',"")
        quoted_string = "&".join("{0}={1}".format(k,quote_plus(v)) for k,v in unsigned_items)

        #获取最终的订单信息字符串
        signed_string = quoted_string + "&sign="+quote_plus(sign)
        return signed_string

    def order_data(self, data):
        """对参数按字母序排序，并处理字典类型的值"""
        # 1. 识别字典类型的值
        complex_keys = []
        for key, value in data.items():
            if isinstance(value, dict):
                complex_keys.append(key)
        
        # 2. 将字典转换为JSON字符串
        for key in complex_keys:
            # 支付宝要求JSON字符串是紧凑格式，无空格
            data[key] = json.dumps(data[key], ensure_ascii=False, separators=(',', ':'))
        
        # 3. 按key字母顺序排序
        return sorted(data.items())
    
    def verify_signature(self, params):
        """验证支付宝回调签名"""
        # 1. 提取签名和签名类型
        sign = params.get('sign')
        sign_type = params.get('sign_type', 'RSA2')
        
        if not sign:
            return False
        
        # 2. 移除签名相关参数，准备验证数据
        params_to_verify = {}
        for key, value in params.items():
            if key not in ['sign', 'sign_type']:
                params_to_verify[key] = value
        
        # 3. 对参数排序
        sorted_items = self.order_data(params_to_verify)
        
        # 4. 构建待验证字符串
        sign_string = "&".join("{0}={1}".format(k, v) for k, v in sorted_items)
        
        # 5. Base64解码签名
        try:
            sign_bytes = base64.b64decode(sign)
        except:
            return False
        
        # 6. 使用支付宝公钥验证签名
        verifier = PKCS1_v1_5.new(self.ali_pub_key)
        digest = SHA256.new(sign_string.encode('utf-8'))
        
        try:
            return verifier.verify(digest, sign_bytes)
        except:
            return False
    
    def get_payment_url(self, signed_string):
        """获取完整的支付URL"""
        return f"{self.__gateway}?{signed_string}"