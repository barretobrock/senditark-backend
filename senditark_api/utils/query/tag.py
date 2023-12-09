from typing import (
    Dict,
    List,
)

from sqlalchemy.orm import Session

from senditark_api.model import TableTag
from senditark_api.utils.query.base import (
    BaseQueryHelper,
    FilterListType,
    ModelDictType,
)


class TagQueries(BaseQueryHelper):

    @classmethod
    def add_tag(cls, session: Session, data: ModelDictType) -> TableTag:
        return cls._add_obj(session=session, obj_class=TableTag, data=data)

    @classmethod
    def get_tag(cls, session: Session, tag_id: int = None, filters: FilterListType = None) -> TableTag:
        if filters is None:
            filters = [TableTag.tag_id == tag_id]
        return cls._get_obj(session=session, obj_class=TableTag, filters=filters)

    @classmethod
    def get_tags(cls, session: Session, filters: FilterListType = None, limit: int = 100) -> List[TableTag]:
        return cls._get_objs(session=session, obj_class=TableTag, filters=filters, limit=limit)

    @classmethod
    def edit_tag(cls, session: Session, tag_id: int, data: ModelDictType):
        tag_obj = cls.get_tag(session=session, tag_id=tag_id)
        if tag_obj is None:
            raise ValueError(f'Failed to find tag with id: {tag_id}')

        cls._edit_obj(session=session, obj=tag_obj, data=data)

    @classmethod
    def get_tag_data(cls, session: Session, tag_id: int = None, tag_obj: TableTag = None) -> Dict:
        if tag_obj is None:
            tag_obj = cls.get_tag(session=session, tag_id=tag_id)

        return {
            'tag_id': tag_obj.tag_id,
            'tag_name': tag_obj.tag_name,
            'tag_color': tag_obj.tag_color
        }

    @classmethod
    def delete_tag(cls, session: Session, tag_id: int):
        cls.log.info(f'Handling DELETE for TAG ({tag_id})')

        tag = cls.get_tag(session=session, tag_id=tag_id)

        session.delete(tag)
        session.commit()


if __name__ == '__main__':
    from senditark_api.config import DevelopmentConfig

    DevelopmentConfig.build_db_engine()
    session = DevelopmentConfig.SESSION()
    tq = TagQueries
    tag = session.query(TableTag).filter(TableTag.tag_id == 2).one_or_none()
