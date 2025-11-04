from datetime import datetime
from io import BytesIO
import pandas as pd
from fastapi.responses import StreamingResponse
import requests
import pyqrcode
from io import BytesIO
from PIL import Image
import base64



def download_dataframe_as_xlsx(df, filename):

    buffer = BytesIO()
    with pd.ExcelWriter(buffer) as writer:
        if isinstance(df, list):
            df = pd.DataFrame(df)
        if isinstance(df, tuple):
            df = df[0].reset_index()
        df.to_excel(writer, index=False)

    time = datetime.today().strftime("%d-%m-%y %H-%M-%S")
    return StreamingResponse(
        BytesIO(buffer.getvalue()),
        media_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
        headers={
            'Access-Control-Expose-Headers': 'Content-Disposition',
            'Content-Disposition': f'attachment; filename="{filename} - {time}.xlsx"'},
    )


def get_data_location(pr_id: str = "0", tr_id: str = "0", zs_id: str = "0", fosa_id: str = "0", zs_filter: int = 0):

    selectedkeyLabel = 'district_name'

    if fosa_id != "0":
        selectedkeyLabel = 'fullname'
    elif zs_id != "0":
        selectedkeyLabel = 'facility_name'
    elif tr_id != "0":
        selectedkeyLabel = 'health_area_name'

    elif (pr_id != '0'):
        selectedkeyLabel = 'county_name'
        if zs_filter == 1:
            selectedkeyLabel = "health_area_name"
    else:
        selectedkeyLabel = 'district_name'

    return selectedkeyLabel


def is_datetime(value):
    return isinstance(value, datetime)

def generate_qr_code(data: str):
    c = pyqrcode.create(data)
    s = BytesIO()
    c.png(s,scale=6)
    encoded = base64.b64encode(s.getvalue()).decode("ascii")
    return encoded


def format_datetime(value, format='%d-%m-%y'):
    return value.strftime(format)