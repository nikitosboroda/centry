from sqlalchemy import and_
from uuid import uuid4
from werkzeug.datastructures import FileStorage
from json import loads
from plugins.base.utils.restApi import RestResource
from plugins.base.utils.api_utils import build_req_parser, get

from ..models.api_tests import SecurityApiTests


class SecurityTestsApi(RestResource):
    _get_rules = (
        dict(name="offset", type=int, default=0, location="args"),
        dict(name="limit", type=int, default=0, location="args"),
        dict(name="search", type=str, default="", location="args"),
        dict(name="sort", type=str, default="", location="args"),
        dict(name="order", type=str, default="", location="args"),
        dict(name="name", type=str, location="args"),
        dict(name="filter", type=str, location="args")
    )

    _post_rules = (
        dict(name="name", type=str, location='form'),
        dict(name="urls_to_scan", type=str, location='form'),
        dict(name="urls_exclusions", type=str, location='form'),
        dict(name="scanners_cards", type=str, location='form'),
        # dict(name="reporting_cards", type=str, location='form'),
        dict(name="reporting", type=str, location='form'),
        dict(name="save_and_run", type=str, location='form')
    )

    # _delete_rules = (
    #     dict(name="id[]", type=int, action="append", location="args"),
    # )

    def __init__(self):
        super().__init__()
        self.__init_req_parsers()

    def __init_req_parsers(self):
        self.get_parser = build_req_parser(rules=self._get_rules)
        self.post_parser = build_req_parser(rules=self._post_rules)
        # self.delete_parser = build_req_parser(rules=self._delete_rules)

    def get(self, project_id: int):
        args = self.get_parser.parse_args(strict=False)
        reports = []
        total, res = get(project_id, args, SecurityApiTests)
        for each in res:
            reports.append(each.to_json())
        return {"total": total, "rows": reports}

    # def delete(self, project_id: int):
    #     args = self.delete_parser.parse_args(strict=False)
    #     project = self.rpc.project_get_or_404(project_id=project_id)
    #     query_result = SecurityApiTests.query.filter(
    #         and_(SecurityApiTests.project_id == project.id, SecurityApiTests.id.in_(args["id[]"]))
    #     ).all()
    #     for each in query_result:
    #         each.delete()
    #     return {"message": "deleted"}

    def post(self, project_id: int):
        args = self.post_parser.parse_args(strict=False)

        save_and_run = args.pop("save_and_run")
        if save_and_run:
            # TODO: write test running
            ...

        project = self.rpc.project_get_or_404(project_id=project_id)

        test = SecurityApiTests(
            project_id=project.id,
            test_uid=str(uuid4()),
            name=args["name"],
            urls_to_scan=loads(args["urls_to_scan"]),
            urls_exclusions=loads(args["urls_exclusions"]),
            scanners_cards=loads(args["scanners_cards"]),
            reporting=loads(args["reporting"])
        )

        test.insert()
        return test.to_json(exclude_fields=("id",))