def get_route_for_eval_type(eval_type):
    if eval_type == 1:
        return "studentmgr:api_view"

    if eval_type == 2:
        return "studentmgr:container_view"

    if eval_type == 3:
        return "studentmgr:code_eval_view"

    if eval_type == 4:
        return "studentmgr:container_eval_view"

    if eval_type == 5:
        return "studentmgr:scale_eval_view"
