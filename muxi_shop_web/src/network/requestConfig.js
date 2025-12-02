import axios from 'axios'; //不加{} 导入export default的内容
import store from '@/store';

export function request(config){
    const instance = axios.create({
        // baseURL:'http://192.168.1.119:8000',
        baseURL:process.env.VUE_APP_BASE_URL,
        timeout:5000,
    })

    //请求拦截
    instance.interceptors.request.use(request=>{
        //一般来说我们会在这里边给一些实例加上token
        const token = window.localStorage.getItem("token")
        if(token){ //如果token存在
            request.headers.Authorization = token
        }
        //直接放行
        return request
    },err=>{
        //这里写一些错误代码

    })

    //响应拦截
    instance.interceptors.response.use(response=>{
        if(response.data.status==false){ //如果用户认证失效（比如token过时）
            window.localStorage.setItem("token","")
            store.commit("setIsLogin",false)
        }
        return response.data?response.data:response;
    },err=>{
        //响应错误在这里处理，比如404 500这些特殊状态码
        //这里跳转一个特殊的处理页面

    })
    return instance(config);
}