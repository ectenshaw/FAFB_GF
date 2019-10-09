import psycopg2
import json
import re
import requests
import psycopg2

num = '[-+]?[0-9]*.?[0-9]+'
bbox_re = r'BOX3D\(({0})\s+({0})\s+({0}),\s*({0})\s+({0})\s+({0})\)'.format(num)


def getPrimaryVolumes(project_id):
    '''
        Helper function that returns list of all volumes considered as primary neuropils
        by using the standardized volume naming schema to filter out the others - modified version of get_volume_details

    '''
    params = {
        'project_id': project_id
    }

    query = '''
    SELECT id, project_id, name, comment, user_id, editor_id,
                 creation_time, edition_time, Box3D(geometry), ST_Asx3D(geometry)
             FROM catmaid_volume v
             WHERE v.project_id= %(project_id)s AND
                  (name LIKE '%%_R' OR name LIKE '%%_L' OR char_length(name)<5) AND char_length(name) <= 10 AND
                   name NOT LIKE 'v14%%'
    '''

    cursor = connection.cursor()
    cursor.execute(query, params)
    volume = cursor.fetchall()

    return volume


def makeVolumeBB(project_id):
    '''
        Helper function - Directly copied from within the get_volume_details functions - just wrapped it
        would include information on all relevant neuropils
    '''
    myTupList = []
    v = getPrimaryVolumes(project_id)
    for volume in v:

        # Parse bounding box into dictionary, coming in format "BOX3D(0 0 0,1 1 1)"
        bbox_matches = re.search(bbox_re, volume[8])
        if not bbox_matches or len(bbox_matches.groups()) != 6:
            raise ValueError("Couldn't create bounding box for geometry")
        bbox = list(map(float, bbox_matches.groups()))
        myTuple = {
            'id': volume[0],
            'project_id': volume[1],
            'name': volume[2],
            'comment': volume[3],
            'user_id': volume[4],
            'editor_id': volume[5],
            'creation_time': volume[6],
            'edition_time': volume[7],
            'bbox': {
                'min': {'x': bbox[0], 'y': bbox[1], 'z': bbox[2]},
                'max': {'x': bbox[3], 'y': bbox[4], 'z': bbox[5]}
            },
            'mesh': volume[9]
        }
        myTupList.append(myTuple)
    return myTupList


def getBBintersections(project_id):
    '''
    helper function that returns paramSet - a dictionary of dictionaries as:
    {'volume name' : {'project_id':int,'minx':float, 'miny':float, 'minz':float, 'maxx':float, 'maxy':float,
     'maxz':float, 'halfzdiff':float, 'min_nodes': int, 'min_cable':int}}

    '''
    volumeSet = makeVolumeBB(project_id)
    paramSet = {}
    for volume in volumeSet:
        params = {
            'project_id': project_id
        }
        bbmin, bbmax = volume['bbox']['min'], volume['bbox']['max']
        params['minx'] = bbmin['x']
        params['miny'] = bbmin['y']
        params['minz'] = bbmin['z']
        params['maxx'] = bbmax['x']
        params['maxy'] = bbmax['y']
        params['maxz'] = bbmax['z']

        params['halfzdiff'] = abs(params['maxz'] - params['minz']) * 0.5
        params['halfz'] = params['minz'] + (params['maxz'] - params['minz']) * 0.5
        params['min_nodes'] = 1  # int(data.get('min_nodes', 0))
        params['min_cable'] = 1  # int(data.get('min_cable', 0))
        # params['skeleton_ids'] = get_request_list(data, 'skeleton_ids', map_fn=int)
        paramSet[volume['name']] = params

    return paramSet


@api_view(['GET', 'POST'])
@requires_user_role(UserRole.Browse)
def skeletonInnervations(paramSet, skeleton_ids):
    '''
        Test environment only contains two skeletons - based on that, sql query always returns list of all
        SKIDs but all data (about both skeletons) is contained in the first SKID in the list - if this changes,
        write an else statement for: len(cleanResults) >1.
        ---
        parameters:
            - name: skeleton_ids
            - required: True
            - type: array [int]
    '''
    skeleton_ids = skeleton_ids
    skelVols = {}
    myResults = {}
    for i in skeleton_ids:
        myResults[str(i)] = {}
        skelVols[str(i)] = []

    for params in paramSet:
        extra_where = []
        extra_joins = []

        paramSet[params]['skeleton_ids'] = skeleton_ids
        needs_summary = paramSet[params]['min_nodes'] > 0 or paramSet[params]['min_cable'] > 0

        # extra_joins.append(skeletonIDs)
        if paramSet[params]['min_nodes'] > 1:
            extra_where.append("""
                css.num_nodes >= %(min_nodes)s
            """)
        if needs_summary:
            extra_joins.append("""
                JOIN catmaid_skeleton_summary css
                    ON css.skeleton_id = skeleton.id
            """)
        if paramSet[params]['min_cable'] > 0:
            extra_where.append("""
                css.cable_length >= %(min_cable)s
            """)
        if skeleton_ids:
            extra_joins.append("""
                        JOIN UNNEST(%(skeleton_ids)s::int[]) query_skeleton(id)
                            ON query_skeleton.id = skeleton.id
                    """)
        node_query = """
                    SELECT DISTINCT t.skeleton_id
                    FROM (
                      SELECT te.id, te.edge
                        FROM treenode_edge te
                        WHERE floatrange(ST_ZMin(te.edge),
                             ST_ZMax(te.edge), '[]') && floatrange(%(minz)s, %(maxz)s, '[)')
                          AND te.project_id = %(project_id)s
                      ) e
                      JOIN treenode t
                        ON t.id = e.id
                      WHERE e.edge && ST_MakeEnvelope(%(minx)s, %(miny)s, %(maxx)s, %(maxy)s)
                        AND ST_3DDWithin(e.edge, ST_MakePolygon(ST_MakeLine(ARRAY[
                            ST_MakePoint(%(minx)s, %(miny)s, %(halfz)s),
                            ST_MakePoint(%(maxx)s, %(miny)s, %(halfz)s),
                            ST_MakePoint(%(maxx)s, %(maxy)s, %(halfz)s),
                            ST_MakePoint(%(minx)s, %(maxy)s, %(halfz)s),
                            ST_MakePoint(%(minx)s, %(miny)s, %(halfz)s)]::geometry[])),
                            %(halfzdiff)s)
                """
        if extra_where:
            extra_where = 'WHERE ' + '\nAND '.join(extra_where)
        else:
            extra_where = ''
        query = """
            SELECT skeleton.id
            FROM (
                {node_query}
            ) skeleton(id)
            {extra_joins}
            {extra_where}
        """.format(**{
            'extra_joins': '\n'.join(extra_joins),
            'extra_where': extra_where,
            'node_query': node_query,
        })
        cursor = connection.cursor()
        cursor.execute(query, paramSet[params])
        for i in myResults:
            myResults[i][params] = cursor.fetchall()

    cleanedResults = {}
    for i in myResults:
        for item in myResults[i]:
            if len(myResults[i][item]) >= 1:
                cleanedResults[i] = myResults[i]
                break
    if (len(cleanedResults)) == 1:
        cleanedResults = cleanedResults[list(cleanedResults.keys())[0]]
        cleanResults = {}
        for bb in cleanedResults:
            if len(cleanedResults[bb]) > 0:
                cleanResults[bb] = cleanedResults[bb]
                for tup in cleanResults[bb]:
                    skelVols[str(tup[0])].append(bb)

    # insert else statement here if data returned does not match test environment

    return skelVols