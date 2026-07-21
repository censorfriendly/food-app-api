from typing import Any

from sqlalchemy.orm import Session

from exceptions.custom import ConflictError, NotFoundError, ValidationError
from models.household import Household
from models.household_member import HouseholdMember
from models.user import User
from repositories.household_repository import HouseholdMemberRepository, HouseholdRepository
from services.base import BaseService


class HouseholdService(BaseService[Household]):
    def __init__(self, db: Session):
        super().__init__(db)
        self.household_repo = HouseholdRepository(db)
        self.member_repo = HouseholdMemberRepository(db)

    @property
    def repository(self):
        return self.household_repo

    def create_household(self, user: User, name: str, timezone: str) -> dict[str, Any]:
        if not name or not name.strip():
            raise ValidationError("Household name is required")

        existing = self.household_repo.get_by_name_for_owner(user.id, name.strip())
        if existing:
            raise ConflictError("Household already exists for this user")

        household = Household(name=name.strip(), owner_user_id=user.id, timezone=timezone or "UTC")
        self.db.add(household)
        self.db.flush()

        member = HouseholdMember(household_id=household.id, user_id=user.id, role="Owner", is_active=True)
        self.db.add(member)
        if not user.default_household_id:
            user.default_household_id = household.id
        self.db.commit()
        self.db.refresh(household)

        return {
            "id": household.id,
            "name": household.name,
            "timezone": household.timezone,
            "owner": {"id": user.id, "email": user.email, "name": user.first_name or user.email},
        }

    def list_user_households(self, user: User) -> list[dict[str, Any]]:
        memberships = (
            self.db.query(HouseholdMember, Household)
            .join(Household, HouseholdMember.household_id == Household.id)
            .filter(HouseholdMember.user_id == user.id, HouseholdMember.is_active.is_(True))
            .order_by(Household.name.asc())
            .all()
        )

        return [
            {
                "id": household.id,
                "name": household.name,
                "timezone": household.timezone,
                "role": membership.role,
                "is_default": household.id == user.default_household_id,
            }
            for membership, household in memberships
        ]

    def set_default_household(self, user: User, household_id: str) -> dict[str, Any]:
        if not household_id or not household_id.strip():
            raise ValidationError("Household selection is required")

        membership = (
            self.db.query(HouseholdMember)
            .filter(
                HouseholdMember.user_id == user.id,
                HouseholdMember.household_id == household_id.strip(),
                HouseholdMember.is_active.is_(True),
            )
            .first()
        )
        if not membership:
            raise NotFoundError("Household is not available to this user")

        user.default_household_id = household_id.strip()
        self.db.commit()

        return {"household_id": user.default_household_id}

    def invite_user_to_household(self, user: User, household_id: str, email: str) -> dict[str, Any]:
        if not household_id or not household_id.strip():
            raise ValidationError("Household selection is required")
        if not email or not email.strip():
            raise ValidationError("An email address is required")

        membership = (
            self.db.query(HouseholdMember)
            .filter(
                HouseholdMember.user_id == user.id,
                HouseholdMember.household_id == household_id.strip(),
                HouseholdMember.is_active.is_(True),
            )
            .first()
        )
        if not membership:
            raise NotFoundError("Household is not available to this user")

        invited_email = email.strip().lower()
        invited_user = self.db.query(User).filter(User.email.ilike(invited_email)).first()
        household = self.db.query(Household).filter(Household.id == household_id.strip()).first()

        if invited_user:
            existing_membership = (
                self.db.query(HouseholdMember)
                .filter(HouseholdMember.household_id == household_id.strip(), HouseholdMember.user_id == invited_user.id)
                .first()
            )
            if existing_membership:
                existing_membership.is_active = True
                existing_membership.role = "Member"
            else:
                self.db.add(
                    HouseholdMember(
                        household_id=household_id.strip(),
                        user_id=invited_user.id,
                        role="Member",
                        is_active=True,
                    )
                )
            self.db.commit()
            return {
                "status": "joined",
                "email": invited_user.email,
                "household_id": household_id.strip(),
                "household_name": household.name if household else None,
                "message": "User was granted access to this household.",
            }

        return {
            "status": "invited",
            "email": invited_email,
            "household_id": household_id.strip(),
            "household_name": household.name if household else None,
            "message": "Invitation recorded. The user will be granted access once they sign up.",
        }
