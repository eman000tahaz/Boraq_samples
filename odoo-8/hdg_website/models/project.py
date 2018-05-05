from openerp.osv import fields, osv

class project(osv.osv):
    _inherit = 'project.project'

    def get_address(self, cr, uid, context=None):
        address_obj =  self.pool.get('project.project')
        address_search = address_obj.search(cr, uid,[])
        project = []
        for ad in address_search:
            temp = {}
            record = address_obj.browse(cr, uid,ad ,context=context)
            temp['name']= record.name
            if(record.address):
                temp['address']=record.address
            else:
                temp['address']='Egypt'
            temp['image']=record.image
            print temp
            project.append(temp)
        return project
