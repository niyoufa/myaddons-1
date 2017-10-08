#coding=utf-8

from openerp.osv import osv,fields
from openerp import tools, api
from openerp.tools.translate import _
import pdb,time,datetime

#odootask.task
class Task(osv.osv):
    _inherit = "mail.thread"
    _name = "odootask.task"

    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)

    def create(self, cr, uid, vals, context=None):
        curr_time = str(datetime.datetime.now())
        vals["number"] = curr_time.replace("-", "").replace(" ", "").replace(":", "").replace(".", "")
        res = super(Task, self).create(cr, uid, vals, context=context)
        return res

    def write(self,cr,uid,ids,vals,context=None):
        context = context or {}
        if vals.has_key("id"):
            ids = [vals["id"]]
        res = super(Task, self).write(cr,uid,ids,vals,context=context)
        return res

    _columns = {

        'number':fields.char('Number'),

        'out_trade_no':fields.char("OutTradeNo"),
        'pay_state':fields.char("PayState"),
       
        'community': fields.many2one("odootask.community"),
        'category_id':fields.many2one('odootask.task_category'),
        'amount':fields.float(),
        'unit':fields.many2one("odootask.unit"),
        'donator_id':fields.many2one("res.partner"),
        'donate_time':fields.datetime("Donate Time"),
        'donee_id':fields.many2one('odootask.donatee'),
        'donee_type':fields.many2one('odootask.donee_type'),
        'remark':fields.char('Remark'),
        'track':fields.one2many('odootask.track','number'),

        'state':fields.selection(
            [("confirmed", "等待入库"), ("done", "完成收入"), ("draft", "取消收入")], default="confirmed"),

        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'odootask.task': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'odootask.task': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),

        'image_path':fields.char("图片地址"),
        "image_url":fields.char("图片查询url"),
    }

class Grant(osv.osv):
    _inherit = "mail.thread"
    _name = "odootask.grant"

    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)

    def create(self, cr, uid, vals, context=None):
        # {'message_follower_ids': False, 'remark': False, 'create_date': '2016-10-26 08:04:50', 'track': [],
        #  'state': 'confirmed', 'amount': 1, 'donee_id': 2, 'category_id': 3, 'message_ids': False}
        context = context or {}

        # 自动生成编号
        curr_time = str(datetime.datetime.now())
        number = curr_time.replace("-","").replace(" ","").replace(":","").replace(".","")
        vals["number"] = number

        # 参数验证
        if uid == 1:
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"社区用户才可以创建发放",))
        category_id = vals.get("category_id")
        if not category_id:
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"请选择种类",))
        if not vals.get("amount"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"发放数量错误",))
        if not vals.get("donee_id"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"请选择受赠人",))
        if not vals.get("create_date"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"请选择时间",))

        # 检查库存
        category = self.pool.get("odootask.task_category").browse(cr,uid,[category_id],context=None)
        amount = category.amount
        donee_amount = vals.get("amount")
        if donee_amount > amount:
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"库存不足",))

        user_obj = self.pool.get("res.users").browse(cr,uid,[uid],context=context)
        category = self.pool.get("odootask.task_category").browse(cr,uid,[category_id],context=context)
        if category:
            vals["unit"] = category.unit.id
        else:
            vals["unit"] = False

        vals["community"] = user_obj.community.id
        res = super(Grant, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        grant = self.browse(cr, uid, ids[0:1], context)[0]

        # 参数验证
        if vals.has_key("category_id") and not vals.get("category_id"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"请选择种类",))
        if vals.has_key("amount") and not vals.get("amount"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"发放数量错误",))
        elif vals.has_key("amount"):
            # 检查库存
            category_id = vals.get("category_id",False)
            if not category_id:
                category_id = grant.category_id.id
            category = self.pool.get("odootask.task_category").browse(cr, uid, [category_id], context=None)
            amount = category.amount
            curr_donee_amount = grant.amount
            donee_amount = vals.get("amount")
            if donee_amount > curr_donee_amount + amount:
                raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"库存不足",))

        if vals.has_key("donee_id") and not vals.get("donee_id"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"请选择受赠人",))
        if vals.has_key("create_date") and not vals.get("create_date"):
            raise osv.except_osv(_('Warning!'), _("create error: '%s'") % (u"请选择时间",))

        if vals.has_key("category_id"):
            category_id = vals.get("category_id")
            if category_id == False:
                raise osv.except_osv(_('Warning!'), _("create group error: '%s'") % (u"请选择种类",))
            else:
                category = self.pool.get("odootask.task_category").browse(cr, uid, [category_id], context=context)
                if category:
                    vals["unit"] = category.unit.id
                else:
                    vals["unit"] = False
        if uid != 1:
            user_obj = self.pool.get("res.users").browse(cr, uid, [uid], context=context)
            vals["community"] = user_obj.community.id
        res = super(Grant, self).write(cr, uid, ids, vals, context=context)
        return res

    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        res = super(Grant, self).unlink(cr, uid, ids, context=context)
        return res

    def search(self, cr, uid, args, offset=0, limit=None, order=None, context=None):
        context = context or {}
        res = super(Grant, self).search(cr, uid, args, offset=offset, limit=limit, order=order, context=context)
        return res

    def read(self, cr, uid, ids, fields=None, context=None, load='_classic_read'):
        context = context or {}
        res = super(Grant, self).read(cr, uid, ids, fields=fields, context=context, load=load)
        return res

    _columns = {
        'number':fields.char("编号"),
        'community': fields.many2one("odootask.community"),
        'category_id': fields.many2one('odootask.task_category'),
        'amount': fields.float(),
        'unit': fields.many2one("odootask.unit"),
        'donee_id': fields.many2one('odootask.donatee'),
        'donee_type': fields.many2one('odootask.donee_type'),
        'remark': fields.char('Remark'),
        'track': fields.one2many('odootask.track', 'grant_number'),

        'state': fields.selection(
            [("confirmed", "等待发放"), ("done", "完成发放"), ("draft", "取消发放")], default="confirmed"),

        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
                               help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
                                        string="Medium-sized image", type="binary", multi="_get_image",
                                        store={
                                            'odootask.grant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                        },
                                        help="Medium-sized image of this contact. It is automatically " \
                                             "resized as a 128x128px image, with aspect ratio preserved. " \
                                             "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
                                       string="Small-sized image", type="binary", multi="_get_image",
                                       store={
                                           'odootask.grant': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
                                       },
                                       help="Small-sized image of this contact. It is automatically " \
                                            "resized as a 64x64px image, with aspect ratio preserved. " \
                                            "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),

        'image_path': fields.char("图片地址"),
        "image_url": fields.char("图片查询url"),
    }

# 志愿者
class GoodPartner(osv.osv):
    _name = "res.partner"
    _inherit = "res.partner"

    def write(self,cr,uid,ids,vals,context=None):
        context = context or {}
        if vals.has_key("id"):
            ids = [vals["id"]]
        res = super(GoodPartner, self).write(cr,uid,ids,vals,context=context)
        return res

    _columns = {
        'number':fields.char("编号"),
        'partner_type':fields.selection([("donator", "志愿者"),("donatee","受赠人")]),
        'cardid':fields.char("身份证"),
        'goods':fields.one2many("odootask.task","donator_id"),
        'donatee_goods':fields.one2many("odootask.task","donee_id"),
    }

# 受赠人、捐赠者
class Donatee(osv.osv):
    _name = "odootask.donatee"

    _columns = {
        'name':fields.char('姓名'),
        'phone':fields.char('手机号'),
        'partner_type': fields.selection([("donator", "志愿者"), ("donatee", "受赠人")]),
        'cardid': fields.char("身份证"),
        'donatee_goods': fields.one2many("odootask.task", "donee_id"),
        'address':fields.char("地址"),
        'donatee_type':fields.many2one("odootask.donatee_type", "人员类别"),
    }

# odootask.task_category
class TaskCategory(osv.osv):
    _name = "odootask.task_category"
    _order = 'donator_amount desc'

    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)

    def donator_amount_func(self,cr,uid,ids,field_name,args,context):
        res = {}
        for category in self.browse(cr,uid,ids,context=None):
            domain = [("community","=",category.community.id),("category_id","=",category.id)]
            task_ids = self.pool.get("odootask.task").search(cr,uid,domain)
            tasks = self.pool.get("odootask.task").browse(cr,uid,task_ids,context)
            donator_amount = 0.0
            for task in tasks:
                donator_amount += task.amount
            res[category.id] = donator_amount
        return res

    def donatee_amount_func(self, cr, uid, ids, field_name, args, context):
        res = {}
        for category in self.browse(cr, uid, ids, context=None):
            domain = [("community", "=", category.community.id), ("category_id", "=", category.id)]
            grant_ids = self.pool.get("odootask.grant").search(cr, uid, domain)
            grants = self.pool.get("odootask.grant").browse(cr, uid, grant_ids, context)
            donatee_amount = 0.0
            for grant in grants:
                donatee_amount += grant.amount
            res[category.id] = donatee_amount
        return res

    def amount_func(self, cr, uid, ids, field_name, args, context):
        res = {}
        for category in self.browse(cr, uid, ids, context=None):
            domain = [("community", "=", category.community.id), ("category_id", "=", category.id)]
            task_ids = self.pool.get("odootask.task").search(cr, uid, domain)
            tasks = self.pool.get("odootask.task").browse(cr, uid, task_ids, context)
            grant_ids = self.pool.get("odootask.grant").search(cr, uid, domain)
            grants = self.pool.get("odootask.grant").browse(cr, uid, grant_ids, context)
            amount = 0.0
            for task in tasks:
                amount += task.amount
            for grant in grants:
                amount -= grant.amount
            res[category.id] = amount
        return res

    _columns = {
        'name':fields.char('名称'),
        'unit':fields.many2one('odootask.unit',"计量单位"),
        'community': fields.many2one("odootask.community"),
        'task_ids':fields.one2many('odootask.task','category_id'),

        'donator_amount':fields.function(donator_amount_func,
                                         type='float',method=True),
        'donatee_amount':fields.function(donatee_amount_func,
                                         type='float',method=True),
        'amount':fields.function(amount_func,
                                         type='float',method=True),

        'source':fields.char(string='商品来源'),
        'price':fields.float(string='义捐价格',default=0.0),
        'status':fields.selection(
            [("used","启用"), ("unused","禁用")], default="used"),
        'priority':fields.integer(string="优先级", default=1),

        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'odootask.task_category': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'odootask.task_category': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
    }

# odootask.task_comment
class Comment(osv.osv):
    _name = "odootask.task_comment"

    _columns = {
        'content':fields.char('Content'),
        'task_id':fields.many2one('odootask.task'),
    }

class DoneeType(osv.osv):
    _name = "odootask.donee_type"

    _columns = {
        'name':fields.char('名称'),
    }

class Unit(osv.osv):
    _name = "odootask.unit"

    _columns = {
        'name':fields.char('名称'),
    }

class Community(osv.osv):
    _name = "odootask.community"

    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)

    _columns = {
        'name':fields.char('名称'),
        'number':fields.char('编号'),
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'odootask.community': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'odootask.community': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),

        'image_path':fields.char("图片地址"),
        "image_url":fields.char("图片查询url"),
    }

class Track(osv.osv):
    _name = "odootask.track"

    @api.multi
    def _get_image(self, name, args):
        return dict((p.id, tools.image_get_resized_images(p.image)) for p in self)

    @api.one
    def _set_image(self, name, value, args):
        return self.write({'image': tools.image_resize_image_big(value)})

    @api.multi
    def _has_image(self, name, args):
        return dict((p.id, bool(p.image)) for p in self)


    _columns = {
        'number':fields.many2one('odootask.task'),
        'grant_number':fields.many2one('odootask.grant'),
        'type':fields.many2one('odootask.track_type'),
        'time':fields.datetime('Time'),
        'desc':fields.text("备注"),
        
        # image: all image fields are base64 encoded and PIL-supported
        'image': fields.binary("Image",
            help="This field holds the image used as avatar for this contact, limited to 1024x1024px"),
        'image_medium': fields.function(_get_image, fnct_inv=_set_image,
            string="Medium-sized image", type="binary", multi="_get_image",
            store={
                'odootask.track': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Medium-sized image of this contact. It is automatically "\
                 "resized as a 128x128px image, with aspect ratio preserved. "\
                 "Use this field in form views or some kanban views."),
        'image_small': fields.function(_get_image, fnct_inv=_set_image,
            string="Small-sized image", type="binary", multi="_get_image",
            store={
                'odootask.track': (lambda self, cr, uid, ids, c={}: ids, ['image'], 10),
            },
            help="Small-sized image of this contact. It is automatically "\
                 "resized as a 64x64px image, with aspect ratio preserved. "\
                 "Use this field anywhere a small image is required."),
        'has_image': fields.function(_has_image, type="boolean"),
    }

class TrackType(osv.osv):
    _name = "odootask.track_type"

    _columns = {
        'name':fields.char('名称'),
        'desc':fields.text('描述'),
        'community': fields.many2one("odootask.community"),
    }


# 用户
class CommunityUser(osv.osv):
    _name = "res.users"
    _inherit = "res.users"

    _columns = {
        'community':fields.many2one("odootask.community","社区"),
    }

# 人员类别
class DonateeType(osv.osv):
    _name = "odootask.donatee_type"

    _columns = {
        'name':fields.char("名称"),
        'desc':fields.text("描述"),
    }
