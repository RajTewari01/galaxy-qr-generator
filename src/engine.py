import urllib.parse
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.colormasks import (
    RadialGradiantColorMask, VerticalGradiantColorMask,
    HorizontalGradiantColorMask, SquareGradiantColorMask
)
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer

INPUT_MAP = {
    "Website/URL": ["Paste URL"],
    "Wi-Fi Config": ["SSID (Network Name)", "Password", "Type (WPA/WEP)"],
    "Plain Text": ["Enter Text"],
    "vCard (Contact)": ["Full Name", "Phone", "Email", "Organization"],
    "Send SMS": ["Phone Number", "Message"],
    "Send Email": ["To Email", "Subject", "Body"],
    "WhatsApp Msg": ["Phone (w/ Country Code)", "Message"],
    "YouTube Video": ["Video ID"],
    "UPI (India)": ["UPI ID", "Payee Name", "Amount (Optional)"],
    "Geo Coords": ["Latitude", "Longitude"],
}


class QrLogic:
    def format_data(self, mode, i):
        try:
            if not i or not i[0]:
                return "Empty"
            if mode == "Website/URL" or mode == "Plain Text":
                return i[0]
            if mode == "Wi-Fi Config":
                return f"WIFI:S:{i[0]};T:{i[2]};P:{i[1]};;"
            if mode == "Send SMS":
                return f"SMSTO:{i[0]}:{i[1]}"
            if mode == "Send Email":
                return f"mailto:{i[0]}?subject={i[1]}&body={i[2]}"
            if mode == "WhatsApp Msg":
                return f"https://wa.me/{i[0]}?text={urllib.parse.quote(i[1])}"
            if mode == "UPI (India)":
                return f"upi://pay?pa={i[0]}&pn={urllib.parse.quote(i[1])}"
            return i[0]
        except Exception:
            return "Error"

    def generate_image(self, data, gradient_type, colors):
        qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_H)
        qr.add_data(data)
        qr.make(fit=True)

        mask_map = {
            "Radial": RadialGradiantColorMask, "Vertical": VerticalGradiantColorMask,
            "Horizontal": HorizontalGradiantColorMask, "Square": SquareGradiantColorMask
        }

        rgb_colors = []
        for c in colors:
            if isinstance(c, str):
                c_str = str(c).lstrip('#')
                # Use string indexing, correctly handle formatting
                rgb_colors.append(
                    tuple(int(c_str[i:i + 2], 16) for i in (0, 2, 4)))
            else:
                rgb_colors.append((c.red(), c.green(), c.blue()))

        bg = rgb_colors[0]
        c_start = rgb_colors[1]
        c_end = rgb_colors[2]

        mask_cls = mask_map.get(gradient_type, RadialGradiantColorMask)
        if mask_cls is None:
            mask_cls = RadialGradiantColorMask

        if gradient_type == "Vertical":
            mask = mask_cls(
                back_color=bg,
                top_color=c_start,
                bottom_color=c_end)
        elif gradient_type == "Horizontal":
            mask = mask_cls(
                back_color=bg,
                left_color=c_start,
                right_color=c_end)
        else:
            mask = mask_cls(
                back_color=bg,
                center_color=c_start,
                edge_color=c_end)

        img = qr.make_image(
            image_factory=StyledPilImage,
            module_drawer=RoundedModuleDrawer(),
            color_mask=mask
        )
        return img
