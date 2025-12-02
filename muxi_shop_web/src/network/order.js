import { request } from "./requestConfig"; //加{} 导入export {具体名称}的内容

export function createOrderData(data){
    return request({
        url:"/order/",
        method:'post',
        data
    })
}

export function getAllOrders(data){
    return request({
        url:"/order?pay_status=" + data,
        method:'get',
    })
}

export function deleteOrders(data){
    return request({
        url:"/order/delete",
        method:'post',
        data:{ trade_no: data }
    })
}

export function getAllOrdersByTradeNo(data){
    return request({
        url:"/order/goods/?trade_no=" + data,
        method:'get',
    })
}

export function updateOrderInfoData(data){
    return request({
        url:"/order/update/",
        method:'post',
        data
    })
}

export function toAliPayPage(data){
    return request({
        url:"/pay/alipay",
        method:'post',
        data
    })
}