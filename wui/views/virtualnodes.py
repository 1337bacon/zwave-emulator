# -*- coding: utf-8 -*-     
from zwemulator.wui.zwemulatorwui import app
from flask import render_template, request, flash, jsonify #, redirect, url_for
#from flask_login import login_required

from zwemulator.lib.manager import Manager
import json

@app.route('/virtualnodes')
def virtualnodes():
    manager =  Manager()
    return render_template('virtualnodes.html',
        mactive="virtualnodes",
        manager = manager, 
        listdrivers = manager.drivers, 
        listnodes=manager._nodes
        )

@app.route('/virtualnodes/<node_ref>')
def virtualnode(node_ref):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None :
        return render_template('virtualnode.html',
            mactive="virtualnodes",
            active = 'home',
            node_ref = node_ref,
            node = node
            )
    return json.dumps({ "error": "Virtual Node not find" }), 500 

@app.route('/virtualnodes/<node_ref>/cmd_classes', methods=['GET', 'POST'])
def virtualnode_cmdClasses(node_ref):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None:
        if request.method == 'POST':
#            clss = node.getCmdClass(int(request.form['clssId']))
            if 'manufacturerId' in request.form:
                try :
                    node.SetManufacturerId(int(request.form['manufacturerId'], 16))
                    flash(u"Manufactured id is changed to : {0}".format(request.form['manufacturerId']), 'success')
                except :
                    flash(u"ERROR: You must enter an hexadecimal format ({0})".format(request.form['manufacturerId']), 'error')
            elif 'manufacturerName' in request.form:
                node.SetManufacturerName(request.form['manufacturerName'])
                flash(u"Manufactured name is changed to : {0}".format(request.form['manufacturerName']), 'success')
            else :
                flash(u"Requête inconnue : {0}".format(request.form), 'error')
        return render_template('virtualnode_cmd_classes.html',
            mactive="virtualnodes",
            active = 'cmd_classes',
            node_ref = node_ref,
            node = node
            )
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref) }), 500 
    
@app.route('/virtualnodes/<node_ref>/update_clss')
def virtualnode_cmdClasse_update(node_ref):
    inputId = request.args.get('inputId', 0, type=str)
    clssId = request.args.get('clssId', 0, type=int)
    key = request.args.get('key', 0, type=str)
    value = request.args.get('value', 0, type=str)
    print "Update cms clss :", clssId,  key, value
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None:
        clss = node.getCmdClass(int(clssId))
        result = 'success'
        if type(value) == str: value = u"{0}".format(value)
        if key == 'issupported' :
            msg = u"Cmd clss supported is changed to : {0}".format(value)
            if value == 'true' : clss.m_getSupported = True
            elif value == 'false' : clss.m_getSupported = False
            else : 
                msg = u"ERROR: Not true/false format ({0})".format(value)
                result = 'error'
                value = clss.m_getSupported
        elif key == 'version' :
            clss.m_version = value
            msg = u"Cmd clss version is changed to : {0}".format(value)
        elif key == 'manufacturerId' :
            try :
                node.SetManufacturerId(int(value, 16))
                msg = u"Manufactured id is changed to : {0}".format(value)
            except :
                msg = u"ERROR: You must enter an hexadecimal format ({0})".format(value)
                result = 'error'
                value = node.GetManufacturerId
        elif key == 'manufacturerName' :
            node.SetManufacturerName(value)
            msg = u"Manufactured name is changed to : {0}".format(value)
        elif key == 'productType':
            try :
                node.SetProductType(int(value, 16))
                msg = u"ProductType is changed to : {0}".format(value)
            except :
                msg = u"ERROR: You must enter an hexadecimal format ({0})".format(value)
                result = 'error'
                value = node.GetProductType
        elif key == 'productId':
            try :
                node.SetProductId(int(value, 16))
                msg = u"Product id is changed to : {0}".format(value)
            except :
                msg = u"ERROR: You must enter an hexadecimal format ({0})".format(value)
                result = 'error'
                value = node.GetProductId
        elif key[:4] == 'grp_':
            indexGrp = int(key[4:])
            result,  error = clss.SetGroupKey(indexGrp, 'label', value)
            if result : 
                msg = u"Label group {0} is changed to : {1}".format(indexGrp,  value)
            else :
                result = 'error'
                msg = u"Label group {0} can't set to : {1} - {2}".format(indexGrp, value, error)
                value = clss.getGroup(indexGrp)['label']
        elif key[:4] == 'max_':
            indexGrp = int(key[4:])
            try :
                result,  error = clss.SetGroupKey(indexGrp, 'max_associations', int(value))
                if result:
                    msg = u"max_associations group {0} is changed to : {1}".format(indexGrp,  value)
                else :
                    result = 'error'
                    msg = u"max_associations group {0} can't set to : {1} - {2}".format(indexGrp, value, error)
                    value = clss.groups(indexGrp)['max_associations']
            except :
                msg = u"ERROR: You must enter number ({0})".format(value)
                result = 'error'
                value = clss.getGroup(indexGrp)['max_associations']
        elif key[:9] == 'grpNodes_':
            indexGrp = int(key[9:])
            try :
                value = value.split(',')
                result,  error = clss.SetGroupKey(indexGrp, 'nodes', [int(i) for i in value])
                if result:
                    msg = u"nodes in group {0} are changed to : {1}".format(indexGrp,  value)
                else :
                    result = 'error'
                    msg = u"nodes in group {0} can't set to : {1} - {2}".format(indexGrp, value, error)
                    value = clss.groups(indexGrp)['nodes']
            except :
                msg = u"ERROR: bad format of list of nodes ({0})".format(value)
                result = 'error'
                value = clss.getGroup(indexGrp)['nodes']
        elif key[:10] == 'endPindex_':
            id = int(key[10:])
            num = 1
#            instance = {}
            for i,  ep in  clss._node.getAllInstance().iteritems() :
                if num == id : 
                    try :
                        result,  error = clss._node.setInstanceIndex(i, int(value))
                        if result:
                            msg = u"instance {0} index is changed to : {1}".format(id,  value)
                        else :
                            result = 'error'
                            msg = u"instance {0} index can't set to : {1} - {2}".format(id, value, error)
                            value = i
                        break
                    except :
                        msg = u"ERROR: You must enter number ({0})".format(value)
                        result = 'error'
                        value = i
                        break
                num +=1
        elif key[:5] == 'endP_':
            id = int(key[5:])
            num = 1
#            instance = {}
            for i,  ep in  clss._node.getAllInstance().iteritems() :
                if num == id : 
                    try :
                        result,  error = clss._node.setInstanceEndPoint(i, int(value))
                        if result:
                            msg = u"instance {0} EndPoint is changed to : {1}".format(id,  value)
                        else :
                            result = 'error'
                            msg = u"instance {0} EndPoint can't set to : {1} - {2}".format(id, value, error)
                            if i in clss._node.mapEndPoints : value = clss._node.mapEndPoints[i].keys()[0]
                            else : value = '255'
                        break
                    except :
                        msg = u"ERROR: You must enter number ({0})".format(value)
                        result = 'error'
                        if i in clss._node.mapEndPoints : value = clss._node.mapEndPoints[i].keys()[0]
                        else : value = '255'
                        break
                num +=1
        elif key[:9] == 'clssEndP_':
            id = int(key[9:])
            num = 1
#            instance = {}
            for i,  ep in  clss._node.getAllInstance().iteritems() :
                if num == id : 
                    endP = ep[ep.keys()[0]]
                    try :
                        value = value.split(',')
                        value = [int(v, 16) for v in value]
                    except :
                        value = []
                    result,  error = clss._node.setInstanceClssEndPoint(i, ep.keys()[0], value)
                    if result:
                        msg = u"Class of instance {0} are changed to : {1}".format(id,  value)
                    else :
                        result = 'error'
                        msg = u"Class of instance {0} can't set to : {1} - {2}".format(id, value, error)
                        if i in clss._node.mapEndPoints : value = clss._node.mapEndPoints[i][endP]
                        else : value = []
                    break
                num +=1
        else :
            msg = u"Resquest not handled actually : {0}, value : {1}".format(key,  value)
            result = 'error'
        return jsonify(inputId = inputId, value=value, result=result,  msg=msg)
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref) }), 500 

@app.route('/virtualnodes/<node_ref>/config', methods=['GET', 'POST'])
def virtualnode_configs(node_ref):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None :
        return render_template('virtualnode_config.html',
            mactive="virtualnodes",
            active = 'config',
            node_ref = node_ref,
            node = node
            )
    return json.dumps({ "error": "Virtual Node not find" }), 500 


@app.route('/virtualnodes/<node_ref>/update_config_poll')
def virtualnode_cmdClasse_update_config_poll(node_ref):
    inputId = request.args.get('inputId', 0, type=str)
#    clssId = request.args.get('clssId', 0, type=int)
    key = request.args.get('key', 0, type=str)
    value = request.args.get('value', 0, type=str)
#    instance = int(request.args.get('instance', 0, type=str))
#    label = request.args.get('label', 0, type=str)
    idPoll = int(request.args.get('idPoll', 0, type=str))
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    poll = node.getPoll(idPoll)
    if node is not None :
        if poll is not None :
            print "Update config for polled clss :", poll['cmdclass'],  key, value, poll['instance']
            result = 'success'
            data = []
            if type(value) == str: value = u"{0}".format(value)
            if key[:6] == 'unable':
                value = 'start'
                if node.setPollParam(idPoll, 'unable', True):
                    msg = u"Start poll for cmdclass: {0}, instance: {1}".format(poll['cmdclass'], poll['instance'])
                else :
                    msg = u"Poll doesn't exist : {0}, id : {1}".format(poll['cmdclass'],  idPoll)
                    result = 'error'
            elif key[:7] == 'disable':
                value = 'stop'
                if node.setPollParam(idPoll, 'unable', False):
                    msg = u"Stop poll for cmdclass: {0}, instance: {1}".format(poll['cmdclass'], poll['instance'])
                else :
                    msg = u"Poll doesn't exist : {0}, id : {1}".format(poll['cmdclass'],  idPoll)
                    result = 'error'
    #        elif key[:7] == 'clss_P-':
    #            value = int(clssId)
    #            if node.setPollParam(idPoll, 'cmdclass', node.getCmdClass(value).GetCommandClassName):
    #                msg = u"Changed cmdclass for poll cmdclass: {0}, instance: {1}".format(clssId, instance)
    #                for v in node.getCmdClassValues(value) :
    #                    if  v.instance == instance : data.append({"instance": v.instance, "label": v.label, "index": v.index, "units": v.units})
    #                print "Set data", data
    #            else :
    #                msg = u"Poll doesn't exist : {0}, id : {1}".format(clssId,  idPoll)
    #                result = 'error'
    #        elif key[:11] == 'clss_lab_P-':
    #            value = label
    #            if node.setPollParam(idPoll, 'label', value):
    #                msg = u"Changed label for poll cmdclass: {0}, instance: {1}".format(clssId, instance)
    #            else :
    #                msg = u"Poll doesn't exist : {0}, id : {1}".format(clssId,  idPoll)
    #                result = 'error'
    #        elif key[:8] == 'instance':
    #            value = int(value)
    #            if node.setPollParam(idPoll, 'instance', value):
    #                msg = u"Changed instance for poll cmdclass: {0}, instance: {1}".format(clssId, instance)
    #            else :
    #                msg = u"Poll doesn't exist : {0}, id : {1}".format(clssId,  idPoll)
    #                result = 'error'
            elif key[:6] == 'timing':
                value = int(value)
                if node.setPollParam(idPoll, 'timing', value):
                    msg = u"Changed timing for poll cmdclass: {0}, instance: {1}".format(poll['cmdclass'], poll['instance'])
                else :
                    msg = u"Poll doesn't exist : {0}, id : {1}".format(poll['cmdclass'],  idPoll)
                    result = 'error'
            elif key[:11] == 'params':
#                params = request.args.get('params', 0, type=str)
                print "******************************************"
                print request.args.items()
                print request.form
                params = json.loads(request.args.get('params'))
                print "*********", params
                find = True
                if value == 'values':
                    poll['params']['values'] = params
                else :
                    find = False
                    msg = u"key value not handle : {0}, params : {1}".format(value, params)
                    result = 'error'
                if find :
                    if node.setPollParam(idPoll, 'params', poll['params']):
                        msg = u"Changed parameters for poll: {0}".format(poll)
                    else :
                        msg = u"Error on setting paramaters '{0}': {1}".format(value, poll['params'])
                        result = 'error'
            else:
                msg = u"Resquest not handled actually : {0}, value : {1}".format(key,  value)
                result = 'error'
        else:
            return json.dumps({ "error": "poll with id {0} doesn't exist for Virtual Node {1}.".format(idPoll,  node_ref) }), 500 
        return jsonify(inputId = inputId, value=value, result=result,  msg=msg,  idPoll=idPoll, data=data)
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref) }), 500 
    
@app.route('/virtualnodes/<node_ref>/<clssId>/get_label')
def virtualnode_cmdClasse_get_label(node_ref, clssId):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    instance = int(request.args.get('instance', 0, type=str))
    label = request.args.get('label', 0, type=str)
    labels =[]
    instances = []
    if node is not None : 
        print type(clssId),  clssId
        try:
            clssId = int(clssId)
        except:
            clssId = manager.GetCommandClassId(clssId)
        print type(clssId),  clssId
        for v in node.getCmdClassValues(int(clssId)) :
            if v.instance not in instances : instances.append(v.instance)
        if instance not in instances : instance = 0
        for v in node.getCmdClassValues(int(clssId)) :
            if (instance == 0) or (v.instance == instance) : labels.append({"instance": v.instance, "label": v.label, "index": v.index, "units": v.units, "type": v.GetType, "genre": v.GetGenre,  "listVal": v.getValuesCollection()})
        return jsonify(result='success', labels=labels, label=label, instances=instances,  instance=instance)
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref)}), 500 

@app.route('/virtualnodes/<node_ref>/<idPoll>/get_poll')
def virtualnode_cmdClasse_get_poll(node_ref, idPoll):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None :
        poll = node.getPoll(int(idPoll))
        if poll is not None :
            params = {}
            clssId = manager.GetCommandClassId(poll['cmdclass'])
            for v in node.getCmdClassValues(int(clssId)) :
                if (v.instance == poll['instance']) :
                    params = {"index": v.index, "units": v.units, "type": v.GetType, "genre": v.GetGenre,  "listVal": v.getValuesCollection()}
            return jsonify(result='success', vpoll=poll, valueparams=params)
        return json.dumps({ "error": "poll with id {0} doesn't exist for Virtual Node {1}.".format(idPoll,  node_ref) }), 500 
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref)}), 500 

@app.route('/virtualnodes/<node_ref>/<clssId>/create_poll')
def virtualnode_cmdClasse_create_poll(node_ref, clssId):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    instance = int(request.args.get('instance', 0, type=str))
    label = request.args.get('label', 0, type=str)
    timing = int(request.args.get('timing', 0, type=str))
    status = request.args.get('status', 0, type=str)
    polltype = request.args.get('polltype', '', type=str)
    mode = request.args.get('mode')
    values = json.loads(request.args.get('values'))
    step = request.args.get('step','')
    print request.args.items()
    print request.form
    print  homeId , nodeId , instance , label , timing,  status, polltype ,  mode , values , step
#    labels =[]
#    instances = []
    if node is not None :
        clss = node.getCmdClass(int(clssId))
        result,  msg = node.addPollValue({'cmdclass':clss.GetCommandClassName, 'instance': instance,'label': label, 'timing': timing,
                                                       'unable': True if status == 'unable' else False,
                                                       'params': { 'polltype': polltype, 
                                                                         'mode': mode, 
                                                                         'values': values, 
                                                                         'step': step}})
        if result == 'error':
            return jsonify(result='error', msg=msg)
        return jsonify(result='success', msg='Poll value created')
#        return render_template('virtualnode_config.html',
#            mactive="virtualnodes",
#            active = 'config',
#            node_ref = node_ref,
#            node = node
#            )
#        return virtualnode_configs(node_ref)
#        return redirect(url_for("/virtualnodes//config",  node_ref = node_ref))
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref)}), 500 

@app.route('/virtualnodes/<node_ref>/delete_poll/<idPoll>')
def virtualnode_cmdClasse_delete_poll(node_ref, idPoll):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None :
        if node.deletePoll(int(idPoll)) : 
            return virtualnode_configs(node_ref)
        else :
            return jsonify(result='error',  msg='poll {0} not find'.format(idPoll),  idPoll=idPoll)
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref) }), 500 

@app.route('/virtualnodes/<node_ref>/create_poll')
def virtualnode_cmdClasse_new_poll(node_ref):
    manager =  Manager()
    homeId = node_ref.split(".")[0]
    nodeId = int(node_ref.split(".")[1])
    node = manager.getNode(homeId, nodeId)
    if node is not None :
        return render_template('virtualnode_newpoll.html',
            mactive="virtualnodes",
            active = 'config',
            node_ref = node_ref,
            node = node
            )
    return json.dumps({ "error": "Virtual Node {0} not find.".format(node_ref) }), 500 

# jinja 2 filters

def renderCmdClssGeneric(clss):
    render = u'<div class="panel panel-default">'
    if clss.GetCommandClassName == "COMMAND_CLASS_ASSOCIATION" :
        render += '<table id="tabgroup_{0}" class="table table-condensed">' + \
                       '<thead class="bghead">' +\
                        '<tr>' +\
                          '<th class="col-md-5 text-center">Group label</th>' +\
                          '<th class="col-md-3 text-center">Max members</th>' +\
                          '<th class="col-md-4 text-center" title="Nodes list separate by ,">Nodes include</th>' + \
                        '</tr>' +\
                      '</thead>' +\
                    '<tbody class="bgbody2">'.format(clss.nodeId)
        print "render groups : ",  clss.groups
        for gr in clss.groups:
            listNodes = []
            for nId in clss._node._manager.getListNodeId(clss.homeId):
                if nId != clss.nodeId:
                    listNodes.append({"value": nId,
                                             "label": "%.3d - %s"%(nId, clss._node._manager.getNode(clss.homeId,  nId).name),
                                             "textButton": nId})
            render += '<tr>'
            render += renderFormInputText("grp_{0}".format(gr["index"]), gr["label"], clss.GetCommandClassId, "",
                                                    "col-md-5", "col-md-5", "col-md-25").replace('<div', '<td', 1).replace('</form></div>', '</form></td>')
            render += renderFormInputText("max_{0}".format(gr["index"]), gr["max_associations"], clss.GetCommandClassId, "",
                                                    "col-md-3", "col-md-5", "col-md-12").replace('<div', '<td', 1).replace('</form></div>', '</form></td>')
            render += renderFormInputSelect("grpNodes_{0}".format(gr["index"]), gr["nodes"], clss.GetCommandClassId, listNodes, "",
                                                    "col-md-4", "col-md-5", "col-md-12",  "multiple").replace('<div', '<td', 1).replace('</form></div>', '</form></td>')
            render += '</tr>'
        render += '</tbody>' +\
                    '</table>' +\
                '</div>'
    elif clss.GetCommandClassName == "COMMAND_CLASS_MULTI_INSTANCE" :
        render += '<table id="tabgroup_{0}" class="table table-condensed">' + \
                       '<thead class="bghead">' +\
                        '<tr>' +\
                          '<th class="col-md-2 text-center">Instance</th>' +\
                          '<th class="col-md-2 text-center">Index</th>' +\
                          '<th class="col-md-2 text-center" title="Value 255 for main instance">EndPoint</th>' + \
                          '<th class="col-md-4 text-center">Cmnd Class</th>' + \
                        '</tr>' +\
                      '</thead>' +\
                    '<tbody class="bgbody2">'.format(clss.nodeId)
        num = 1
        instances = clss._node.getAllInstance()
        for index in instances: #clss._node.mapEndPoints:
            instance = instances[index] #clss._node.mapEndPoints[index]
            print "Render instance End Point :",  index, instance
            render += '<tr>'
            render += '<td class="vert-align text-center col-md-1">{0}</td>'.format(num)
#            render += renderFormInputText("num_{0}".format(num), num, clss.GetCommandClassId, "",
#                                                    "col-md-5", "col-md-5", "col-md-25").replace('<div', '<td', 1).replace('</form></div>',  '</form></td>')
            render += renderFormInputText("endPindex_{0}".format(num), index, clss.GetCommandClassId, "",
                                                    "col-md-2", "col-md-5", "col-md-12").replace('<div', '<td', 1).replace('</form></div>', '</form></td>')
            for eP in instance:
                render += renderFormInputText("endP_{0}".format(num), eP, clss.GetCommandClassId, "",
                                                    "col-md-2", "col-md-5", "col-md-12").replace('<div', '<td', 1).replace('</form></div>', '</form></td>')
                if eP == 255: 
                    render += u'<td class="vert-align col-md-4 text-center">Main instance, no EndPoint</td>'
                else :
                    listCmdClasses = []
                    for index in clss._node._manager.cmdClassRegistered.m_commandClasses:
                        c = clss._node._manager.cmdClassRegistered.m_commandClasses[index]
                        listCmdClasses.append({"value": c.StaticGetCommandClassId,
                                                         "label": "0x%.2x - %s"%(c.StaticGetCommandClassId, c.StaticGetCommandClassName),
                                                         "textButton": "0x%.2x"%c.StaticGetCommandClassId})
                    listCmdClasses.sort()
                    render += renderFormInputSelect("clssEndP_{0}".format(num), instance[eP], clss.GetCommandClassId, listCmdClasses, "",
                                                    "col-md-4", "col-md-5", "col-md-12",  "multiple").replace('<div', '<td', 1).replace('</form></div>', '</form></td>')
                
            render += '</tr>'
            num += 1
        render += '</tbody>' +\
                    '</table>' +\
                '</div>'
    elif clss.GetCommandClassName == "COMMAND_CLASS_MANUFACTURER_SPECIFIC":
        render += '<div class="row">'
        render += renderFormInputText("manufacturerId", clss._node.GetManufacturerId, clss.GetCommandClassId, "Manufacturer&nbspID:",
                                                    "col-md-6", "col-md-5", "col-md-7")
        render += renderFormInputText("manufacturerName", clss._node.GetManufacturerName, clss.GetCommandClassId, "Name:",
                                                    "col-md-6", "col-md-2", "col-md-10")
        render += '</div>'
        render += '<div class="row">'
        render += renderFormInputText("productId", clss._node.GetProductId, clss.GetCommandClassId, "Product&nbspID:",
                                                    "col-md-6", "col-md-5", "col-md-7")
        render += renderFormInputText("productType", clss._node.GetProductType, clss.GetCommandClassId, "Type:",
                                                    "col-md-6", "col-md-2", "col-md-7")
        render += '</div>'
        render += '</div>'
    else : 
        render = u'<div class="panel panel-default"></div>'
    return render

def renderFormInputText(idInput, value, clssId, label ="", col = "col-md-6", colLabel = "col-md-5",  colInput = "col-md-7"):
    render = '<div class="{0}">'.format(col) +\
                            '<form method="POST" action="" class="form-inline">' +\
                              '<div class="form-group">'
    if label : render += '<label class="{0} control-label vert-align" for="{1}">{2}</label>'.format(colLabel, idInput, label)
    render +=              '<div class="{0}">'.format(colInput) +\
                                 '<div class="input-group">' +\
                                   '<input type="text" name="{0}" id="{0}" class="form-control" value="{1}" clssid={2}>'.format(idInput, value, clssId) +\
                                   '<span class="input-group-addon input-addon-xs"><a id="st-{0}" href="#" class="btn btn-xs btn-info"><span id="stic-{0}" class="glyphicon glyphicon-floppy-saved"></span></a></span>'.format(idInput) +\
                            '</div></div></div>' +\
                         '</form></div>'
    return render

def renderFormInputSelect(idInput, value, clssId, options,  label ="", col = "col-md-6", colLabel = "col-md-5",  colInput = "col-md-7",  multiple = ""):
    render = u'<div class="{0}">'.format(col) +\
                            '<form method="POST" action="" class="form-inline">' +\
                              '<div class="form-group">'
    if label : render += u'<label class="{0} control-label vert-align" for="{1}">{2}</label>'.format(colLabel, idInput, label)
    render +=              u'<div class="{0}">'.format(colInput) +\
                                 '<div class="input-group">' +\
                                   '<select {0} ref="mSelect" name="{1}" id="{1}" multiple="multiple" value="{2}" clssid={3}>'.format(multiple, idInput, value, clssId)
    for opt in options:
        if opt['value'] in value : selected = 'selected="true"'
        else : selected = ''
        render += u'<option value="{0}" textButton="{1}" {2}>{3}</option>'.format(opt['value'], opt['textButton'], selected, opt['label'])
    render +=             u'</select><span class="input-addon-xs"><a id="st-{0}" href="#" class="btn btn-xs btn-info"><span id="stic-{0}" class="glyphicon glyphicon-floppy-saved"></span></a></span>'.format(idInput) +\
                            '</div></div></div>' +\
                         '</form></div>'
    return render