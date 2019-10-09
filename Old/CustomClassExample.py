class SkeletonInfo(object):

    connectivity_data = None

    def __init__(self, skeleton_id):
        self.skeleton_id = skeleton_id
        self.n_connections_gf1 = None
        self.n_connections_gf2 = None
        self.annotations = None

        # Initialize from back-end
        if not connectivity_data:
            # Get data from server
            r = requests.get(CATMAID_URL + '...')
            connectivity_data = 1

        # Parse response into fields
        self.n_connections_gf1 = connectivity_data['incoming'][...]


    def get_n_total_connections(self):
        return self.n_connections_gf1 + self.n_connections_gf2

    def __str__(self):
        return "Skeleton {} with connections ...".format(skeleton_id)

class SkeletonInfoBuilder(object):

    def __init__(partner_skeleton_ids):
        self.partner_skeleton_ids = partner_skeleton_ids

    def build(self):
        # Get connectivity data once for all partner skeleton IDs
        request.post('/connectivity', {'skeleton_ids': ...}

        instances = []
        for r in response:
            si = SkeletonInfo(skeleton_id, n1, n2, annotations)

        return instances

builder = SkeletonInfoBuilder([id1, id2])
instances = builder.build()
