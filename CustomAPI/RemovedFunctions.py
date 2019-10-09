def getSkeletonsByAnnotation(annotation=None):
    connection = psycopg2.connect(database="catmaid", user="polskyj", password="Tipitinas1", host="127.0.0.1",
                                  port="5432")
    project_id = project_id
    params = {
        'project_id': project_id
    }
    if annotation is not None:
        query = '''

        '''

    return