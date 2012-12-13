import bleach
import json


def jsonify(data):
    '''
    '''
    return json.dumps(data)


def params(request, dfinc='', dfexc='', dsort='slug'):
    '''
    '''
    try:
        finc = bleach.clean(request.query.fields or dfinc)
        fexc = bleach.clean(request.query.fields or dfexc)
        start = int(bleach.clean(request.query.start or -1))
        size = int(bleach.clean(request.query.size or -1))
        sort = bleach.clean(request.query.sort or dsort)
    except:
        return dfinc.split(','), dfexc.split(','), -1, -1, dsort
    else:
        if finc == '':
            fi = []
        else:
            fi = finc.split(',')
        if fexc == '':
            fe = []
        else:
            fe = fexc.split(',')
        return fi, fe, start, size, sort