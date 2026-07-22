
from sqlalchemy.orm import Session

from models.household import Household
from models.household_member import HouseholdMember
from repositories.base import BaseRepository


class HouseholdRepository(BaseRepository[Household]):
    def __init__(self, db: Session):
        super().__init__(Household, db)

    @property
    def model_type(self):
        return Household

    def get_by_name_for_owner(self, owner_user_id: str, name: str) -> Household | None:
        return self.db.query(Household).filter(Household.owner_user_id == owner_user_id, Household.name == name).first()


class HouseholdMemberRepository(BaseRepository[HouseholdMember]):
    def __init__(self, db: Session):
        super().__init__(HouseholdMember, db)

    @property
    def model_type(self):
        return HouseholdMember
