from models.Complainant import Complainant

complainant = Complainant(
    account_type="facebook",
    account_handle="arush0311",
    complaint_ids=["1234"]
)

complainant.save()