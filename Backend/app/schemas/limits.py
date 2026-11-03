"""Input limits shared by request schemas.

Text length is bounded because queries go to the LLM (cost/quota) and to USIG; coordinates are
bounded to CABA (with a ~2 km margin) because they are accepted from the client as-is.
"""

from typing import Annotated

from pydantic import Field

MAX_QUERY_LENGTH = 500
MAX_ADDRESS_LENGTH = 200
MAX_CODE_LENGTH = 64
MAX_NAME_LENGTH = 128

CABA_LAT_MIN, CABA_LAT_MAX = -34.75, -34.50
CABA_LNG_MIN, CABA_LNG_MAX = -58.56, -58.30

CabaLatitude = Annotated[float, Field(ge=CABA_LAT_MIN, le=CABA_LAT_MAX)]
CabaLongitude = Annotated[float, Field(ge=CABA_LNG_MIN, le=CABA_LNG_MAX)]
