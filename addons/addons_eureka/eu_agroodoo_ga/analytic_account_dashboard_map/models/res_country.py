from odoo import api, fields, models, _
from odoo.http import request

class AccountMove(models.Model):
    _inherit = 'res.country'

    analytic_account_map = fields.Binary(string="File Map JSON")
    analytic_account_map_name = fields.Char(string="Map name")
    analytic_account_map_url = fields.Char(compute="_analytic_account_map_url", store=True)
    analytic_account_map_render = fields.Text(compute="_analytic_account_map_render")

    @api.depends('analytic_account_map_name')
    def _analytic_account_map_url(self):
        for rec in self:
            if rec.analytic_account_map:
                if rec.analytic_account_map_name:
                    rec.analytic_account_map_url = '/web/content/res.country/'+str(rec.id)+'/map/'+rec.analytic_account_map_name+'?download=true&code='+str(rec.code)
                else:
                    rec.analytic_account_map_url = ''
            else:
                rec.analytic_account_map_url = ''

    @api.depends('analytic_account_map_url')
    def _analytic_account_map_render(self):
        for rec in self:
            if rec.analytic_account_map_url:
                rec.analytic_account_map_render = '''
                                <div id="my_map" style="width: 600px;height:450px;"></div>
                                <script type="text/javascript">
                                    var my_map = echarts.init(document.getElementById('my_map'));
                                    my_map.showLoading();
                                    $.get(\''''+rec.analytic_account_map_url+'''\', function (dataJson) {
                                        echarts.registerMap(\''''+rec.name+'''\', dataJson);
                                        var option = {
                                                title: {
                                                    text: \''''+rec.name+'''\',
                                                    left: 'right'
                                                },
                                                tooltip: {
                                                    trigger: 'item',
                                                    showDelay: 0,
                                                    transitionDuration: 0.2,
                                                    formatter: function (params) {
                                                        var value = (params.value + '').split('.');
                                                        value = value[0].replace(/(\d{1,3})(?=(?:\d{3})+(?!\d))/g, '$1,');
                                                        return params.seriesName + '<br/>' + params.name + ': ' + value;
                                                    }
                                                },
                                                series: [
                                                    {
                                                        name: \''''+rec.name+'''\',
                                                        type: 'map',
                                                        roam: true,
                                                        map: \''''+rec.name+'''\',
                                                        emphasis: {
                                                            label: {
                                                                show: true
                                                            }
                                                        }
                                                    }
                                                ]
                                        };
                                        my_map.setOption(option);
                                        my_map.hideLoading();
                                    });
                                    
                                </script>
                                '''
            else:
                rec.analytic_account_map_render = ''

    def get_url_maps(self):
        result = []
        company_ids = self.get_current_company_value()
        company_country_id = 233
        company_default = self.env['res.company'].search([('id', '=', company_ids[0])])
        for company in company_default:
            company_country_id = company.partner_id.country_id.id
        country_ids = self.env['res.country'].search([('analytic_account_map_url','!=','')])
        for c in country_ids:
            if company_country_id == c.id:
                result.append({'country': c.name, 'url': c.analytic_account_map_url })
        for c in country_ids:
            if not company_country_id == c.id:
                result.append({'country': c.name, 'url': c.analytic_account_map_url })
        return result


    def get_current_company_value(self):
        cookies_cids = [int(r) for r in request.httprequest.cookies.get('cids').split(",")] \
            if request.httprequest.cookies.get('cids') \
            else [request.env.user.company_id.id]
        for company_id in cookies_cids:
            if company_id not in self.env.user.company_ids.ids:
                cookies_cids.remove(company_id)
        if not cookies_cids:
            cookies_cids = [self.env.company.id]
        if len(cookies_cids) == 1:
            cookies_cids.append(0)
        return cookies_cids