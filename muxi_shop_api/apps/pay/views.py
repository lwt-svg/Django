from django.http import JsonResponse
from rest_framework.views import APIView
from apps.pay.alipay import Alipay
# Create your views here.


class ToAliPayPageAPIView(APIView):
    def post(self,request):
        # if not request.user.get("status"):
        #     return JsonResponse(request.user,safe=False)
        trade_no = request.data.get("tradeNo")
        total_amount = request.data.get("orderAmount")
        alipay = Alipay()
        url = alipay.direct_pay(
            out_trade_no=trade_no,
            subject = "主题"+trade_no,
            total_amount = total_amount
        )
        re_url = alipay.gateway + "?{data}".format(data=url)
        return JsonResponse({"alipay":re_url})