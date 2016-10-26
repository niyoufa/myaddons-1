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

    def write(self,cr,uid,ids,vals,context=None):
        context = context or {}
        if vals.has_key("id"):
            ids = [vals["id"]]
        res = super(Task, self).write(cr,uid,ids,vals,context=context)
        return res

    _columns = {

        'number':fields.char('Number'),
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
        curr_time = str(datetime.datetime.now())
        number = curr_time.replace("-","").replace(" ","").replace(":","").replace(".","")
        vals["number"] = number
        category_id = vals.get("category_id")
        if not category_id:
            raise osv.except_osv(_('Warning!'), _("create group error: '%s'") % ("请选择种类",))
        user_obj = self.pool.get("res.users").browse(cr,uid,[uid],context=context)
        vals["unit"] = category_id
        vals["community"] = user_obj.community.id
        res = super(Grant, self).create(cr, uid, vals, context=context)
        return res

    def write(self, cr, uid, ids, vals, context=None):
        context = context or {}
        res = super(Grant, self).write(cr, uid, ids, vals, context=context)
        # group_id = ids[0]
        # if vals.has_key("name"):
        #     group_name = vals.get("name", "")
        #     try:
        #         result = Rong.rongyun_group_refresh(group_id=group_id, group_name=group_name)
        #     except Exception, e:
        #         raise osv.except_osv(_('Warning!'), _("create group error: '%s'") % (str(e),))
        #
        # user_id_list = []
        # project = super(dhuiproject, self).browse(cr, uid, ids, context=context)
        # creator = self.pool.get("res.users").browse(cr, uid, [uid], context=context)
        # user_id_list.append(str(creator.user_id or uid))
        # if vals.has_key("user_id"):
        #     user_id = vals["user_id"]
        #     user = self.pool.get("res.users").browse(cr, int(user_id), [int(user_id)], context=context)
        #     user_id_list.append(str(user.user_id or user.id))
        # else:
        #     user_id_list.append(str(project.user_id.user_id or uid))
        # if vals.has_key("members"):
        #     member_id_list = vals["members"][0][2]
        #     mongo_member_id_list = []
        #     for member_id in member_id_list:
        #         member = self.pool.get("res.users").browse(cr, member_id, [member_id], context=context)
        #         mongo_member_id_list.append(str(member.user_id or member.id))
        # user_id_list.extend(mongo_member_id_list)
        #
        # self.join_or_quit_group(user_id_list, group_id)
        return res

    def unlink(self, cr, uid, ids, context=None):
        context = context or {}
        res = super(Grant, self).unlink(cr, uid, ids, context=context)

        # user_obj = self.pool.get('res.users')
        # user = user_obj.read(cr,uid,[uid],context=context)[0]
        # user_id = user["user_id"] or ""
        # try:
        #     result = Rong.rongyun_group_dismiss(user_id=uid, group_id=ids[0])
        # except Exception, e:
        #     raise osv.except_osv(_('Warning!'), _("dismiss group error: '%s'") % (str(e),))
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

# 受赠人
class Donatee(osv.osv):
    _name = "odootask.donatee"

    _columns = {
        'name':fields.char('名称'),
        'phone':fields.char('手机号'),
        'partner_type': fields.selection([("donator", "志愿者"), ("donatee", "受赠人")]),
        'cardid': fields.char("身份证"),
        'donatee_goods': fields.one2many("odootask.task", "donee_id"),
    }

# odootask.task_category
class TaskCategory(osv.osv):
    _name = "odootask.task_category"

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
        'unit':fields.many2one('odootask.unit',"计量单位"),
        'community': fields.many2one("odootask.community"),
        'task_ids':fields.one2many('odootask.task','category_id'),

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

    _columns = {
        'name':fields.char('名称'),
        'number':fields.char('编号'),
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
        'desc':fields.text('Desc'),
        'community': fields.many2one("odootask.community"),
    }


# 用户
class CommunityUser(osv.osv):
    _name = "res.users"
    _inherit = "res.users"

    _columns = {
        'community':fields.many2one("odootask.community","社区"),
    }