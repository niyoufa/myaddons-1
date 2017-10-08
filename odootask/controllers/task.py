#coding=utf-8
__author__ = 'wt'
import openerp.http
from openerp.http import request
from base import odootask_qweb_render
import math
import simplejson as json
import pdb
import requests
import datetime
import json,pdb

from openerp import http
from openerp.http import request
from openerp.http import serialize_exception as _serialize_exception


import status
import utils
import functools
import werkzeug.utils
import werkzeug.wrappers
import simplejson
import logging

_logger = logging.getLogger(__name__)

def serialize_exception(f):
    @functools.wraps(f)
    def wrap(*args, **kwargs):
        res = utils.init_response_data()
        try:
            res = f(*args, **kwargs)
            res["message"] = status.Status().getReason(res["code"])
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["message"] = status.Status().getReason(res["code"])
            _logger.exception("An exception occured during an http request")
            se = _serialize_exception(e)
            error = {
                'code': 200,
                'message': "Odoo Server Error",
                'data': se
            }
            res["error_info"] = error
            response = request.make_response(json.dumps(res),headers={"Access-Control-Allow-Origin":"*"})
            return response
        response = request.make_response(json.dumps(res),headers={"Access-Control-Allow-Origin":"*"})
        return response
    return wrap

class TaskController(openerp.http.Controller):
    @openerp.http.route("/tasks", type='http', auth="none", methods=["GET"])
    def index(self, **kwargs):
        para_keyword = kwargs.get("k", "")
        para_category_id = kwargs.get("c", "")
        para_order = kwargs.get("o", "create_date")
        para_page = kwargs.get("p", "0")
        para_qty_per_page = kwargs.get("n", "10")

        domain = list()
        if para_keyword:
            domain.append(("name", "ilike", para_keyword))
        if para_category_id:
            domain.append(("category_id", "=", int(para_category_id)))

        env = request.env

        page_count = int(math.ceil(env['odootask.task'].sudo().search_count(domain) / float(para_qty_per_page)))

        page = int(para_page)
        qty_per_page = int(para_qty_per_page)
        tasks = env['odootask.task'].sudo().search(domain, order="%s desc" % para_order, offset=page * qty_per_page,
                                                   limit=qty_per_page)

        categories = env["odootask.task_category"].sudo().search([])
        count_for_category = [
            ((cat.name, cat.id),
             env['odootask.task'].sudo().search_count([("name", "ilike", para_keyword), ("category_id", "=", cat.id)]))
            for cat in categories]

        if para_keyword:
            count_for_category = filter(lambda cfc: cfc[1] > 0, count_for_category)
        count_for_category = dict(count_for_category)

        context = dict()
        context["tasks"] = tasks
        context["count_for_category"] = count_for_category

        context["category_id"] = para_category_id
        context["keyword"] = para_keyword
        context["page"] = para_page
        context["main_nav_task_active"] = True
        context["login_redirect"] = "/tasks"
        context["page_count"] = page_count

        return odootask_qweb_render.render("odootask.tasks", context=context)

    @openerp.http.route("/api/tasks", type='http', auth="public", methods=["GET"])
    def api_tasks(self,**kwargs):
        env = request.env
        tasks = env['odootask.task'].sudo().search([])
        j = json.dumps(tasks)
        return "%d" % len(tasks)

    @openerp.http.route("/task/<int:task_id>", type='http', auth="public", methods=["GET"])
    def task(self, task_id=None, **kwargs):
        try:
            if not task_id:
                # TODO return 404
                pass
            env = request.env
            task = env['odootask.task'].sudo().search([("id", "=", task_id)])
            context = dict()
            context["task"] = task
            context["login_redirect"] = "/task/%d" % task_id
            context["ret_url"] = kwargs.get("ret_url")
            context["user_id"] = env.user.id
            return odootask_qweb_render.render("odootask.task", context=context)
        except Exception as e:
            pass

    @openerp.http.route("/task", type='http', auth="user", methods=["GET", "POST"])
    def new_task(self, **kwargs):
        if request.httprequest.method == 'GET':
            try:
                task_categories = request.env["odootask.task_category"].search([]);
                context = dict()
                context["task_categories"] = task_categories
                return odootask_qweb_render.render("odootask.task_new", context=context)
            except Exception as ex:
                pass
                # TODO Error handler
        elif request.httprequest.method == 'POST':
            name = kwargs.get("name", "")
            description = kwargs.get("description", "")
            category_id = kwargs.get("category_id", "")
            values = dict()
            values["name"] = name
            values["description"] = description
            if category_id:
                values["category_id"] = int(category_id)
            request.env["odootask.task"].create(values)
            return "create ok"
        else:
            return "only GET POST is available!"

    @openerp.http.route("/task/apply/<int:task_id>", type='http', auth="user", methods=["GET", "POST"])
    def apply_task(self, task_id=None):
        try:
            if not task_id:
                # TODO return 404
                pass
            env = request.env
            task = env['odootask.task'].sudo().search([("id", "=", task_id)])
            task.apply(env.user.id)
            return "apply ok"
        except Exception as e:
            pass

    @openerp.http.route("/task/<int:task_id>/comment", type='http', auth="user", methods=["POST"])  # "GET",
    def comment(self, task_id=None, **kwargs):
        if request.httprequest.method == 'POST':
            try:
                if not task_id:
                    # TODO return 404
                    pass
                content = kwargs.get("content", "")
                env = request.env
                task = env['odootask.task'].sudo().search([("id", "=", task_id)])
                if task:
                    env["odootask.task_comment"].create({"task_id": task.id, "content": content})
                    return "post comment ok"
            except Exception as e:
                pass

class GoodsController(openerp.http.Controller):
    @openerp.http.route("/MP_verify_UO7AG2TZ01CWYhkZ.txt", type='http', auth="none", methods=["GET"])
    def wx_txt_page(self, **kwargs):
        context = dict()
        return "UO7AG2TZ01CWYhkZ"

    @openerp.http.route("/index.html", type='http', auth="none", methods=["GET"])
    def index_page(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.index", context=context)

    @openerp.http.route("/search.html", type='http', auth="none", methods=["GET"])
    def search_page(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.search", context=context)

    @openerp.http.route("/detail.html", type='http', auth="none", methods=["GET"])
    def detail_page(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.detail", context=context)

    @openerp.http.route("/upload.html", type='http', auth="none", methods=["GET"])
    def upload_page(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.upload", context=context)

    @openerp.http.route("/donator.html", type='http', auth="none", methods=["GET"])
    def donator_page(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.donator", context=context)

    @openerp.http.route("/category_detail.html", type='http', auth="none", methods=["GET"])
    def category_detail(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.category_detail", context=context)

    @openerp.http.route("/more_category.html", type='http', auth="none", methods=["GET"])
    def more_category(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.more_category", context=context)

    @openerp.http.route("/donate_search.html", type='http', auth="none", methods=["GET"])
    def donate_search(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.donate_search", context=context)

    @openerp.http.route("/more_donate.html", type='http', auth="none", methods=["GET"])
    def more_donate(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.more_donate", context=context)

    @openerp.http.route("/pay_donate.html", type="http", auth="none", methods=["GET"])
    def pay_donate(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.pay_donate", context=context)

    @openerp.http.route("/statistic.html", type="http", auth="none", methods=["GET"])
    def statistic(self, **kwargs):
        context = dict()
        return odootask_qweb_render.render("odootask.statistic", context=context)

    @http.route('/good', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def good(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            good_number = kw.get("good_number", "10001")
            task = env['odootask.task'].sudo().search_read([("number", "=", good_number)])
            if len(task) == 0:
                return res
            category_id = task[0]["category_id"][0]
            category_obj = env['odootask.task_category'].sudo().search_read([("id", "=",category_id )])[0]
            if category_obj["unit"] :
                unit = category_obj["unit"]
            else:
                unit = [False,""]
            good = task[0]
            good["unit"] = unit
            good["create_date"] = str(datetime.datetime.strptime(good["create_date"], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(
                    hours=8)).split(".")[0]
            tracks = env['odootask.track'].sudo().search_read([("id", "in", task[0]["track"])],order="%s desc"%"create_date")
            res["data"]["good"] = task[0]
            res["data"]["tracks"] = tracks
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/communitys', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def communitys(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            communitys = env['odootask.community'].sudo().search_read()
            res["data"]["communitys"] = communitys
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/good_types', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def good_types(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            community_id = kw.get("community_id","")
            if community_id !="":
                domain = [("community", "=", int(community_id))]
            else:
                domain = []

            domain.append(("status", "=", "used"))

            good_types = env['odootask.task_category'].sudo().search_read(domain, order="priority asc")
            for good in good_types:
                del good["image"]
                del good["image_small"]
                del good["image_medium"]
            res["data"]["good_types"] = good_types
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/more_good_types', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def more_good_types(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            more = kw.get("more", False)
            page = kw.get("page", 1)
            page_size = kw.get("page_size", 10)
            community_name = kw.get("community_name","")
            if community_name != "":
                domain = [("community.name","ilike",community_name)]
            else:
                domain = []
            good_types = env['odootask.task_category'].sudo().search_read(domain)

            for good in good_types:
                del good["image"]
                del good["image_medium"]
                del good["image_small"]

            if len(good_types):
                good_types.sort(key=lambda obj: obj["donator_amount"])
                good_types.reverse()
                if more:
                    length = len(good_types)
                    pager = utils.count_page(length, page, page_size)
                    good_types = good_types[pager['skip']:pager['skip'] + pager['page_size']]
                    res["data"]["good_types"] = good_types
                    res["pager"] = pager
            else:
                res["data"]["good_types"] = []
                res["pager"] = {}
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/hot_good_types', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def hot_good_types(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            good_types = env['odootask.task_category'].sudo().search_read()
            good_types.sort(key=lambda obj: obj["donator_amount"])
            good_types.reverse()
            good_types = good_types[0:3]
            for good in good_types:
                del good["image"]
                del good["image_medium"]
                del good["image_small"]

            res["data"]["good_types"] = good_types
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/good_type', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def good_type(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            category_id = kw.get("category_id","")
            if category_id != "":
                category_id = int(category_id)
                domain= [("id","=",category_id)]
                good_types = env['odootask.task_category'].sudo().search_read(domain)
                for good in good_types:
                    del good["image"]
                    del good["image_medium"]
                    del good["image_small"]

                res["data"]["good_type"] = good_types[0]
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/donator_number', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def donator_number(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            mobile = kw.get("mobile","")
            if mobile == "":
                raise Exception("请输入手机号")

            donators = env['res.partner'].sudo().search_read([("phone","=",mobile)])
            if len(donators):
                donator = donators[0]
            else:
                donator = {}
            res["data"]["donator"] = donator
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/units', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def units(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            units = env['odootask.unit'].sudo().search_read()
            res["data"]["units"] = units
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/upload', type='http', auth="none", methods=["POST"])
    @serialize_exception
    def upload(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            community_id = kw.get("community_id")
            phone = kw.get("phone","")
            phone_code = kw.get("phone_code","")
            cardid = kw.get("cardid","")
            donator_name = kw.get("donator_name")
            good_type_id = kw.get("good_type")
            good_type_id  = int(good_type_id)
            amount = kw.get("amount")
            remark = kw.get("remark","")
            image_path = kw.get("image_path","")
            image_url = kw.get("image_url","")
            state = "confirmed"
            #存储捐赠人信息
            donators = env['res.partner'].sudo().search_read(["&",("partner_type", "=", "donator"), ("phone","=",phone)])
            if len(donators) > 0 :
                donator = donators[0]
                donaor_number =  donator.get("number","")
                donator_id = donator["id"]

                donator_obj = {}
                donator_obj["id"] = donator_id
                donator_obj["display_name"] = donator_name
                donator_obj["name"] = donator_name
                donator_obj["cardid"] = cardid
                env["res.partner"].sudo().write(donator_obj)
            else:
                donator = dict(
                    display_name = donator_name,
                    name = donator_name,
                    partner_type = "donator",
                    phone = phone,
                    cardid = cardid,
                    goods = [],
                )
                try:
                    env["res.partner"].sudo().create(donator)
                except:
                    pass
                donators = env['res.partner'].sudo().search_read(["&",("partner_type","=","donator")
                ,("phone","=",phone)])
                donator_obj = donators[0]
                donator_obj["number"] = "DR"  + str(donator_obj["id"]).zfill(6)
                donaor_number = donator_obj["number"]
                donator_id = donator_obj["id"]
                env["res.partner"].sudo().write({"id":donator_id,"number":donaor_number})

            community_id = int(community_id)
            community_obj = env['odootask.community'].sudo().search_read([("id","=",community_id)])
            community_numer = community_obj[0]["number"]
            community_id = community_id
            good_type_obj = env['odootask.task_category'].sudo().search_read([("id","=",good_type_id)])

            good = dict(
                donator_id = donator_id,
                category_id = good_type_id,
                unit = good_type_obj[0]["unit"][0],
                amount = amount,
                remark = remark,
                image_path = image_path,
                image_url = image_url,
                state = state,
                community = community_id,
            )
            good_obj = env["odootask.task"].sudo().create(good)
            good_obj = env["odootask.task"].sudo().search_read([("id","=",good_obj.id)])[0]
            good_obj_update = {}
            good_obj_update["id"] = good_obj["id"]
            curr_time = str(datetime.datetime.now())
            good_obj_update["number"] = curr_time.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
            env["odootask.task"].sudo().write(good_obj_update)

            created_goods = env['odootask.task'].sudo().search_read([("id","=",good_obj["id"])])
            res["data"]["good"] = created_goods[0]
            res["data"]["donator_number"] = donaor_number
            # try:
            #     utils.send_106sms(phone,donaor_number)
            # except Exception,e:
            #     print e

        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/goods', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def goods(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            goods = []
            phone = kw.get("phone")
            donators = env['res.partner'].sudo().search_read([("partner_type","=","donator"),("phone", "=", phone)])
            if len(donators) == 0:
                domain = [("number", "=", phone), ("pay_state", "=", "yes")]
                
            else:
                donator = donators[0]
                domain = [("donator_id","=",donator["id"]), ("pay_state", "=", "yes")]

            goods = env["odootask.task"].sudo().search_read(domain)
            if goods:
                goods.sort(key=lambda obj:obj["create_date"])
                goods.reverse()
        
            for good in goods:
                good["create_date"] = str(datetime.datetime.strptime(good["create_date"], "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).split(".")[0]
            res["data"]["goods"] = goods
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/nearby_donate', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def nearby_donate(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            goods = env['odootask.task'].sudo().search_read(["|", ("pay_state", "=", "yes"), ("state", "=", "done")])
            goods.sort(key=lambda obj: obj["create_date"])
            goods.reverse()
            more = kw.get("more",False)
            page = kw.get("page",1)
            page_size = kw.get("page_size",10)
            if more:
                length = len(goods)
                pager = utils.count_page(length, page, page_size)
                goods = goods[pager['skip']:pager['skip']+pager['page_size']]
            else:
                pager = {}
                goods = goods[0:5]

            for good in goods :
                create_date = good["create_date"]
                create_date = str(datetime.datetime.strptime(create_date, "%Y-%m-%d %H:%M:%S") + datetime.timedelta(hours=8)).split(".")[0]
                date = create_date.split(" ")[0]
                time = create_date.split(" ")[1]
                curr_date = str(datetime.datetime.now()).split(" ")[0]
                if date == curr_date :
                    show_date = "今天"
                else:
                    show_date = date.split("-")[1] + "-"+ date.split("-")[2]
                show_time = time.split(":")[0] +":"+ time.split(":")[1]
                good["create_date"] = create_date
                good["show_date"] = show_date
                good["show_time"] = show_time

            res["data"]["goods"] = goods
            res["pager"] = pager
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/image', type='http', auth="none", methods=["GET"])
    def image(self, **kw):
        res = None
        env = request.env
        good_number = kw.get("good_number", "")
        category_id = kw.get("category_id",0)
        image_size = kw.get("image_size", "small") 
        if good_number != "":
            task = env['odootask.task'].sudo().search_read([("number", "=", good_number)])
            if len(task) == 0:
                return res
            tracks = env['odootask.track'].sudo().search_read([("id", "in", task[0]["track"])],
                                                              order="%s desc" % "create_date")
            category_id = task[0]["category_id"][0]
        else:
            category_id = int(category_id)
        category_obj = env['odootask.task_category'].sudo().search([("id", "=", category_id)])
        if image_size == "small":
            image_data = category_obj.image_small
        else:
            image_data = category_obj.image

        import base64
        import hashlib
        headers = [('Content-Type', 'image/png')]
        hashed_session = hashlib.md5(request.session_id).hexdigest()
        retag = hashed_session
        headers.append(('ETag', retag))
        if image_data:
            headers.append(('Content-Length', len(image_data)))
            image_data = base64.b64decode(image_data)
            try:
                ncache = int(kw.get('cache'))
                headers.append(('Cache-Control', 'no-cache' if ncache == 0 else 'max-age=%s' % (ncache)))
            except:
                pass
            return request.make_response(image_data,headers)
        else:
            return request.make_response(image_data, headers)

    @http.route('/donators', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def donators(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            donators = env['res.partner'].sudo().search_read([("partner_type","=","donator")])
            res["data"]["donators"] = donators
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/donator', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def donator(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            phone = kw.get("mobile","")
            donators = env['res.partner'].sudo().search_read(["&",("partner_type","=","donator"),("phone","=",phone)])
            if len(donators):
                donator = donators[0]
            else:
                donator = {}
            res["data"]["donator"] = {}
            res["data"]["donator"]["donator_name"] = donator.get("name","")
            res["data"]["donator"]["cardid"] = donator.get("cardid","")
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    @http.route('/order', type='http', auth='none', methods=["POST"])
    @serialize_exception
    def order(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            openid = kw.get("openid")         
 
            number = kw.get("number")
            order_obj = env['odootask.task'].sudo().search_read([("number", "=", number)])[0]
            pay_state = order_obj["pay_state"]
            if pay_state == "yes":
                return res

            amount = order_obj["amount"]
            category_id = order_obj["category_id"][0]
            good_obj = env['odootask.task_category'].sudo().search_read([("id", "=", category_id)])[0]
            price = good_obj["price"]
            good_name = good_obj["name"]
 
            import requests
            appid = "wx5686b4e04b2a4f66"
            body = "dszyicang-good"
            mch_id = "1401655702"
            device_info = "WEB"
            nonce_str = self.random_str(16)

            out_trade_no = self.md5_data(mch_id + str(datetime.datetime.now()) + nonce_str)
            
            order_update_obj = {}
            order_update_obj["id"] = order_obj["id"]
            order_update_obj["out_trade_no"] = out_trade_no           
            order_update_obj["pay_state"] = "no"
            env["odootask.task"].sudo().write(order_update_obj) 

            total_fee = int( amount * price * 100)
            #total_fee = 1
            spbill_create_ip = "139.224.26.81"
            notify_url = "http://dszyicang.com/notify"
            trade_type = "JSAPI"

            stringA=self.generate_sign(
                appid=appid,
                body=body,
                mch_id=mch_id,
                device_info=device_info,
                nonce_str=nonce_str,
                out_trade_no=out_trade_no,
                total_fee=total_fee,
                spbill_create_ip=spbill_create_ip,
                notify_url=notify_url,
                trade_type=trade_type,
                openid=openid
            )
            secret = "06a9b2dd1d526476ffde40b13419c142"
            stringSignTemp=stringA+"&key=%s"%secret
            sign=self.md5_data(stringSignTemp).upper()

            headers = {'Content-Type': 'application/xml'}
            xml_data = """<xml>
                                    <appid>%s</appid>
                                    <body>%s</body>
                                    <device_info>%s</device_info>
                                    <mch_id>%s</mch_id>
                                    <nonce_str>%s</nonce_str>
                                    <notify_url>%s</notify_url>
                                    <out_trade_no>%s</out_trade_no>
                                    <spbill_create_ip>%s</spbill_create_ip>
                                    <total_fee>%s</total_fee>
                                    <trade_type>%s</trade_type>
                                    <sign>%s</sign>
                                    <openid>%s</openid>
                                 </xml>"""%(appid, body, device_info, mch_id, nonce_str, notify_url, out_trade_no, spbill_create_ip, total_fee, trade_type,                                             sign, openid)
            xml_data = xml_data.replace(" ", "").replace("\n", "")
            response = requests.post("https://api.mch.weixin.qq.com/pay/unifiedorder", data=xml_data, headers=headers)
            res["data"] = response.text 
            print(openid, res)
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        res["data"] = self.parse_xml(res["data"])
        return res

    @http.route('/notify', type='http', auth='none', methods=["POST"])
    @serialize_exception
    def wxpay_notify(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            notify_info = request.httprequest.data
            notify_params = self.parse_notify_xml(notify_info)
            return_code = notify_params["return_code"]
            result_code = notify_params["result_code"]
            out_trade_no =  notify_params["out_trade_no"]
            order_obj = env['odootask.task'].sudo().search_read([("out_trade_no", "=", out_trade_no)])[0]
            order_update_obj = {}
            if return_code == "SUCCESS" and result_code == "SUCCESS" and order_obj["pay_state"] != "yes":
                order_update_obj["pay_state"] = "yes"
                order_update_obj["id"] = order_obj["id"]
                order_update_obj["donate_time"] = str(datetime.datetime.now()).split(".")[0]
                env["odootask.task"].sudo().write(order_update_obj)           
                order_obj = env['odootask.task'].sudo().search_read([("out_trade_no", "=", out_trade_no)])[0]
                mobile = env['res.partner'].sudo().search_read([("id", "=", order_obj["donator_id"][0])])[0]["phone"]
                order_no = order_obj["number"]
                requests.get("http://dszyicang.com:8600/api/donate/success?mobile=%s&order_no=%s"%(mobile, order_no))
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

    def parse_notify_xml(self, data):
        from lxml import etree
        xml = etree.fromstring(data)
        return_code = xml.find("return_code").text
        result_code = xml.find("result_code").text
        out_trade_no = xml.find("out_trade_no").text
        time_end = xml.find("time_end").text
        return dict(
            return_code=return_code,
            result_code = result_code,
            out_trade_no = out_trade_no,
            time_end = time_end
        )

    def parse_xml(self, data):
        from lxml import etree
        xml = etree.fromstring(data)
        return_code = xml.find("return_code").text
        return_msg = xml.find("return_msg").text
        appid = xml.find("appid").text
        mch_id = xml.find("mch_id").text
        device_info = xml.find("device_info").text
        nonce_str = xml.find("nonce_str").text
        sign = xml.find("sign").text
        result_code = xml.find("result_code").text
        prepay_id = xml.find("prepay_id").text
        trade_type = xml.find("trade_type").text
        return dict(
            return_code=return_code,
            return_msg=return_msg,
            appid = appid,
            mch_id = mch_id, 
            device_info = device_info,
            nonce_str = nonce_str,
            sign = sign,
            result_code = result_code,
            prepay_id = prepay_id,
            trade_type = trade_type
        )

    def random_str(self,randomlength=8):
        from random import Random
        str = ''
        chars = 'AaBbCcDdEeFfGgHhIiJjKkLlMmNnOoPpQqRrSsTtUuVvWwXxYyZz'
        length = len(chars) - 1
        random = Random()
        for i in range(randomlength):
            str+=chars[random.randint(0, length)]
        return str

    def md5_data(self, str):
        import hashlib
        m = hashlib.md5()
        m.update(str)
        return m.hexdigest()

    def generate_sign(self, **kwargs):
        params = kwargs.keys()
        sorted_params = sorted(params)
        stringAs = ["%s=%s"%(key, kwargs.get(key)) for key in sorted_params]
        return "&".join(stringAs)

    @http.route('/get_access_token', type='http', auth="none", methods=["GET"])
    @serialize_exception
    def get_access_token(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            code = kw.get("code","")
            import requests
            import json
            response_result = json.loads(requests.get("https://api.weixin.qq.com/sns/oauth2/access_token?appid=wx5686b4e04b2a4f66&secret=93270e940e047d7e1154f7863a6a9b93&code=%s&grant_type=authorization_code"%code).text)
            res["data"] = response_result
            print(res)
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res


    @http.route('/task_statistic', type='http', auth='none', method=["GET"])
    @serialize_exception
    def task_statistic(self, **kw):
        res = utils.init_response_data()
        try:
            env = request.env
            start_time = kw.get("start_time") or "1970-01-01 00:00:00"
            end_time = kw.get("end_time") or str(datetime.datetime.now()).split(".")[0]
            year = int(start_time.split(" ")[0].split("-")[0])
            month = int(start_time.split(" ")[0].split("-")[1])
            day = int(start_time.split(" ")[0].split("-")[2])
            start_time = str(datetime.datetime(year, month, day) - datetime.timedelta(hours=8)).split(".")[0]
         
            year = int(end_time.split(" ")[0].split("-")[0])
            month = int(end_time.split(" ")[0].split("-")[1])
            day = int(end_time.split(" ")[0].split("-")[2])
            end_time = str(datetime.datetime(year, month, day, 23, 59, 59) - datetime.timedelta(hours=8)).split(".")[0]
            tasks = env['odootask.task'].sudo().search_read(["|", ("state", "=", "done"), ("pay_state", "=" , "yes"), ("donate_time", ">=", start_time), ("donate_time", "<=", end_time)])
            res["data"] = {}
            task_list = []
            for task in tasks:
                community = task.get("community")
                donator_id = task.get("donator_id")
                donate_time = task.get("donate_time")
                amount = task.get("amount")
                pay_state = task.get("pay_state")
                category_id = task.get("category_id")
                good_type = env['odootask.task_category'].sudo().search_read([("id", "=", category_id[0])])[0]
                price = good_type.get("price") or 0.0
                task_list.append(dict(
                    community_id = community[0],
                    community = community[1], 
                    donator_id = donator_id[0],
                    donator = donator_id[1],
                    donate_time = donate_time,
                    amount = amount,
                    pay_state = pay_state,
                    category_id = category_id[0],
                    category = category_id[1],
                    total_fee = round(price*amount, 1),
                ))
            category_ids = []
            category_dict = {}
            category_id_dict = {}
            community_ids = []
            community_dict = {}
            community_id_dict = {}
            for task in task_list:
                category_id = task.get("category_id")
                category = task.get("category")
                community = task.get("community")
                community_id = task.get("community_id")
                amount = task.get("amount")
                total_fee = task.get("total_fee")
                if category_id not in category_ids:
                    category_dict[category_id] = amount
                else:
                    category_dict[category_id] += amount
                category_ids.append(category_id)
                category_id_dict[category_id] = category
                
                if community_id not in community_ids:
                    community_dict[community_id] = total_fee
                else:
                    community_dict[community_id] += total_fee
                community_ids.append(community_id)
                community_id_dict[community_id] = community
            
            category_data = sorted(category_dict.iteritems(), key=lambda x:x[1], reverse=True)
            temp_category_data = [ [ category_id_dict[obj[0]], obj[1], obj[0] ] for obj in category_data]
            category_data = temp_category_data

            community_data = sorted(community_dict.iteritems(), key=lambda x:x[1], reverse=True)
            temp_community_data = [ [ community_id_dict[obj[0]], obj[1], obj[0] ] for obj in community_data]
            community_data = temp_community_data
            res["data"] = [category_data, community_data]
        except Exception, e:
            res["code"] = status.Status.ERROR
            res["error_info"] = str(e)
            return res
        return res

