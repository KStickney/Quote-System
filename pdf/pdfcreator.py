import pdfkit, os

# just changed src to href for js files.

# path_wkhtmltopdf = "./bin/wkhtmltopdf.exe"
path_wkhtmltopdf = os.path.join(
    os.path.dirname(os.path.realpath(__file__)), "bin/wkhtmltopdf.exe"
)
config = pdfkit.configuration(wkhtmltopdf=path_wkhtmltopdf)
config.default_options = {"page_size": "Letter", "print_media_type": True, "dpi": 96}

wire_transfer_info = """<tr>
            <td colspan="3" style="font-size:12px;font-family:Times">
                <p style="font-size: 14px; font-weight: bold; text-align: center;">Wire Transfer Information</p>
            </td>
        </tr>
        <tr>
        <td height="45" colspan="2" valign="top" style="font-size: 100%;"><table width="100%" border="0">
                <tr>
                    <th scope="col"> <div align="center" style="border-right: 2px solid #000;">TRW ELECTRIC & SUPPLY COMPANY LLC<br />
                            1106 Great Falls Ct. Unit A<br />
                            Knightdale, NC 27545 USA<br />
                            Tel: 1-800-479-8084<br />
                            <span style="font-weight: bolder;">ATTN: PI 83121-81111</span>
                        </div></th>
                    <th scope="col"><p align="center" style="border-right: 2px solid #000;">TRUIST (BB&amp;T)<br />
                            924 KILDAIRE FARM RD
                            <br />
                            CARY NC 27511-3923 USA<br />
                            TEL 919-319-4820</p></th>
                    <th scope="col"><p align="center">SWIFT CODE: BRBTUS33<br />
                            ABA (ROUTING) # 053101121<br />
                            ACCT# 0005201675253</p></th>
                </tr>
            </table>
        </td>
    </tr>"""


def getHTMLText(
    parts_list,
    quantities_list,
    conditions_list,
    unit_totals_list,
    line_totals_list,
    stocks_list,
    sender,
    sender_email,
    quote_number,
    customer_email,
    subject,
    date,
    payment_method,
    delivery_method,
    additional_notes_list,
    isWireTransfer=False,
    shipping_charges="",
    customer_notes="",
):
    try:

        additional_notes = (
            ""  # TODO: see how get additional notes and change accordingly
        )
        for note in additional_notes_list:
            if note == additional_notes_list[-1]:
                additional_notes += note
            else:
                additional_notes += note + "<br>"

        customer_notes_list = customer_notes.split("\n")
        customer_notes = ""
        for note in customer_notes_list:
            if note == customer_notes_list[-1]:
                customer_notes += note
            else:
                customer_notes += note + "<br>"

        subtotal = 0
        for dol in line_totals_list:
            if dol != "None" and dol != "":
                subtotal += float(dol)

        parts_table = ""
        for i in range(len(parts_list)):
            try:
                parts_table += f"""<tr align = 'center'><td style='text-align: center;'>{i+1}</td><td style='text-align: center;'>{quantities_list[i]}</td><td style='text-align: left;'>{parts_list[i]}</td><td style='text-align: center;'>{conditions_list[i]}</td><td style = 'text-align: center;'>${"{:,.2f}".format(float(unit_totals_list[i]))}</td><td style='text-align: center;'>${"{:,.2f}".format(float(line_totals_list[i]))}</td><td style='text-align: center;'>{stocks_list[i]}</td></tr>"""
            except Exception as e:
                print(e, "table" + str(i))

        if isWireTransfer:
            wire_transfer = wire_transfer_info
            quote_type = "Pro Forma Invoice"
        else:
            wire_transfer = ""
            quote_type = "Quotation"

        current_directory = os.path.dirname(os.path.realpath(__file__))

        if shipping_charges != "":
            shipping_charges = float(shipping_charges.replace(",", "").replace("$", ""))
            total = float(shipping_charges) + subtotal

            shipping_charges = round(shipping_charges, 2)
            shipping_charges = "{:,.2f}".format(shipping_charges)

            shipping_html = f"""
            <tr>
                    <td style="padding-right:3px;height:20px;width:100%;text-align:right;font-size:12px;font-family:Times"><strong>Shipping cost:</strong></td>
                    <td style="white-space:nowrap;padding-right:5px;height:20px;text-align:right;font-size:12px;font-family:Times"><span class="currency">${shipping_charges} USD</span></td>
                </tr>"""
        else:
            shipping_html = ""
            total = subtotal

        subtotal = round(subtotal, 2)
        subtotal = "{:,.2f}".format(subtotal)

        total = round(total, 2)
        total = "{:,.2f}".format(total)

        times_font_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "fonts/Times New Roman/times new roman.ttf",
        )
        gothic_font_path = os.path.join(
            os.path.dirname(os.path.realpath(__file__)),
            "fonts/century-gothic/CenturyGothic.ttf",
        )
        dir_path = str(os.path.dirname(os.path.realpath(__file__)))
        # Times
        html = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <style type="text/css">
                @font-face {{
                FONT-FAMILY: Times;
                src: '{times_font_path}' format('truetype');
                }}
                @font-face {{
                FONT-FAMILY: gothic;
                src: '{gothic_font_path}' format('truetype');
                }}
                BODY {{
                    MARGIN-TOP: 10px;
                    MARGIN-BOTTOM: 10px;
                    MARGIN-LEFT: 10px;
                    MARGIN-RIGHT: 10px;
                    FONT-SIZE: 12px;
                    FONT-FAMILY: Times;
                    PADDING: 0px;
                    BACKGROUND-COLOR: #FFFFFF;
                    COLOR: #000000;
                }}
                TD {{
                    FONT-SIZE: 12px;
                    FONT-FAMILY: gothic;
                    letter-spacing: 0.1em;
                }}
                TH {{
                    FONT-SIZE: 13px;
                    FONT-FAMILY: gothic;
                    letter-spacing: 0.1em;
                }}
                H1 {{
                    FONT-SIZE: 20px;
                    FONT-FAMILY: Times;
                }}
                TABLE,IMG,A {{
                    BORDER: 0px;
                    letter-spacing: 0.1em;
                    FONT-FAMILY: Times;
                }}
                .templateButton{{
                    -moz-border-radius:3px;
                    -webkit-border-radius:3px;
                    /*@editable*/ background-color:#336699;
                    /*@editable*/ border:0;
                    border-collapse:separate !important;
                    border-radius:3px;
                }}
                /**
                * @tab Body
                * @section button style
                * @tip Set the styling for your email's button. Choose a style that draws attention.
                */
                .templateButton, .templateButton a:link, .templateButton a:visited, /* Yahoo! Mail Override */ .templateButton a .yshortcuts /* Yahoo! Mail Override */{{
                    /*@editable*/ color:#FFFFFF;
                    /*@editable*/ font-family:Arial;
                    /*@editable*/ font-size:15px;
                    /*@editable*/ font-weight:bold;
                    /*@editable*/ letter-spacing:-.5px;
                    /*@editable*/ line-height:100%;
                    text-align:center;
                    text-decoration:none;
                }}
            </style>
            <script type='text/javascript' href='{dir_path}/js/jquery/jquery-2.0.0.min.js'></script>
            <script type='text/javascript' href='{dir_path}/js/jquery/jquery-ui-1.10.3.custom.min.js'></script>
            <script type='text/javascript' href='{dir_path}/js/jquery/jquery-migrate-1.1.1.min.js'></script>
            <script type='text/javascript' href='{dir_path}/js/jquery/globalize.js'></script>
            <script type='text/javascript' href='{dir_path}/js/actions.js'></script>
            <!--<script type='text/javascript' src='js/plugins.js'></script>-->
        </head>
        <body style="font-size:12px;font-family:Times;background-color:#FFF;color:#000;margin:10px;padding:0">
        <script type="text/javascript">
            function sendQuoteEmail(qnum) {{
                //alert(qnum);
                $.post('mandrillReSendQuote.php', {{'sendQuote': qnum}}, function (data) {{
                    //alert(data);
                    returnValue = JSON.parse(data);
                    if (returnValue[0].status === "rejected") {{
                        $("#emailAlert").html('<div class="alert alert-error"><strong>Send Error! : ' + returnValue[0].email + '</strong> <br /> Reason: ' + returnValue[0].reject_reason + ' <br /> ID: ' + returnValue[0]._id + '</div>');
                        //document.getElementById('emailAlert').innerHTML = 'Fred Flinstone';
                    }} else {{
                        //$("#emailAlert").html(returnValue);
                        $("#emailAlert").html('<div class="alert alert-success"><strong>Quote Sent! : ' + returnValue[0].email + '</strong> <br /> Status: ' + returnValue[0].status + '<br /> Reason: ' + returnValue[0].reject_reason + ' <br /> ID: ' + returnValue[0]._id + '</div>');
                        //document.getElementById('emailAlert').innerHTML = 'Fred Flinstone  222222';
                    }}
                }});
            }}
        </script>
        <!-- BUTTONS ON TOP
        <span id="printMe" style="color:red; font-weight:900;"><br />
                <FORM>
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" onclick="window.location.href = '/quoteEdit.php?load=82021-63603';" value="Edit Quote" />
                <!--<INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" value="" onclick="sendQuoteEmail('');" value="Resend Quote" />-->             <!--
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" onclick="window.location.href='mandrillReSendQuote.php?sendQuote=82021-63603'" value="E-Mail Quote" />
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none; value=" onClick="window.print()" value="Print View" />
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" onClick="window.opener.location = 'logout.php';window.location.href = 'logout.php?close'" value="Exit" />
                <!--<INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none; value=" onClick="window.location.href = 'logout.php'" value="Done" />-->       <!--
            </FORM>
             <div id="emailAlert" name="emailAlert"></div>
            </span>
        -->
        <table cellspacing="0" cellpadding="0"  style="max-width:960px;background-color:#ffffff;border:0; autosize:2.4;" summary="Order details">
                <tr>
                <td style="font-size:12px; font-family:Times; text-align: right;">
                    <table cellspacing="0" cellpadding="0"  style="width:100%;border:0" summary="Summary">
                        <tr>
                            <td style="vertical-align:top;font-size:12px;font-family:Times">
                                <div id="preview" style="width: 150px;height: 130px;color: #000;background-color: #fff;font-family: Georgia, serif;box-sizing: border-box;position: relative;overflow: hidden;font-size: 64px;"> <div class="element logo-text pre-test" id="sdew_1" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;background-color: rgba(0, 0, 0, 0);font-weight: 200;text-shadow: #333 2px 2px 2px;color: #446094;font-size: 45px;font-family: Georgia, serif;top: 2px;left: 18px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">TRW</p></div>
                                    <div class="element logo-text pre-test" id="sdew_2" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 25px;font-family: Georgia, serif;top: 40px;left: 10px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">ELECTRIC</p></div>
                                    <div class="element logo-text pre-test" id="sdew_3" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 26px;font-family: Georgia, serif;top: 60px;left: 41px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">AND</p></div>
                                    <div class="element logo-text pre-test" id="sdew_3" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 26px;font-family: Georgia, serif;top: 83px;left: 20px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">SUPPLY</p></div>
                                <div class="element logo-text pre-test" id="sdew_3" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 26px;font-family: Georgia, serif;top: 105px;left: 8px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">COMPANY</p></div>
                                </div>
                            </td>
                            <td style="width:100%;padding-left:30px;font-size:12px;font-family:Times">
                                <table cellspacing="0" cellpadding="2" width="100%" summary="Details" style="border:0">
                                    <tr>
                                        <td valign="bottom" align="left" style="font-size:12px;font-family:Times">
                                            <p>                                        1106 Great Falls Ct. Unit A<br />
                                                Knightdale, NC 27545 USA<br />
                                                Tel: 1-800-479-8084<br />
                                                {sender}<br />
                                                Email: <a href="mailto:{sender_email}" style="border:0">{sender_email}<br /> <!-- CHANGE!! -->
                                                </a><a href="http://www.trwsupply.com">www.trwsupply.com</a><br />
                                            </p></td>
                                        <td valign="bottom"><strong  style="font-size: 20px; text-transform: uppercase;">
                                                {quote_type} # <span style="text-decoration: underline;">{quote_number}</span> </strong></td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <hr  style="border: 0px none; border-bottom: 2px solid #58595b; margin: 2px 0px 17px 0px; padding: 0px; height: 0px;"/>
                    <table cellspacing="0" cellpadding="5px" style="border:0;margin-bottom:15px; float:left; width:100%;" summary="Address">
                        <tr>
                            <td width="46%" align="left"><span style="font-size:14px; font-family:Times;"><strong>Customer Information</strong></span></td>
                            <td width="54%" align="left"><span style="font-size:14px; font-family:Times;padding-left:3px;"><strong> Quote Details</strong></span></td>
                        </tr>
                        <tr align="left">
                            <td width="18%" style="font-size:12px;font-family:Times;"><strong>Email: </strong>
                                {customer_email}                    </td>
                            <td style="font-size:12px;font-family:Times;padding-left: 8px;"><strong>Subject: </strong>
                                {subject}</td>
                        </tr>
                        <tr>
                            <td  align="left">{customer_notes}</td>
                            <td><table border="0" style="width:100%;">
                                    <tr>
                                        <td width="174" align="left"><strong>Date:</strong></td>
                                                                        <td width="333" align="left">{date}</td>
                                    </tr>
                                    <tr>
                                        <td align="left"><strong>Payment  Method:</strong></td>
                                        <td align="left"><span>{payment_method}</span></td>
                                    </tr>
                                    <tr>
                                        <td width="174" align="left"><strong style="text-align: right">Delivery Method:</strong></td>
                                        <td width="333" align="left"><span>{delivery_method}</span></td>
                                    </tr>
                                    <!--<tr>
                                        <td width="174" align="left"><strong style="text-align: right">Total Shipping Weight:</strong></td>
                                                                        <td width="333" align="left"><span></span></td>
                                    </tr>-->
                                                            </table>
                            </td>
                        </tr>
                    </table>
                    <table cellspacing="0" cellpadding="3" width="100%" border="1" summary="Products" style="border:0">
                        <tr align="center">
                            <th width="2%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Item</th>
                            <th width="2%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Qty</th>
                            <th width="13%" nowrap="nowrap" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Part #</th>
                            <!--<th width="25%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Description</th>-->
                            <th width="8%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Condition</th>
                                                <th width="5%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Unit Price</th>
                            <th width="5%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Line Total</th>
                            <!--<th width="5%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Wt Ea.</th>-->
                            <th width="12%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Stock</th>
                        </tr>
                        {parts_table}
                    </table>
        
                    <table cellspacing="0" cellpadding="0" width="100%" border="0" id="html_order_info_total" summary="Total" style="border:0">
                        <tr>
                            <td height="4" colspan="2" style="font-size:12px;font-family:Times"></td>
                        </tr>
                        <tr>
                            <td style="padding-right:3px;height:20px;width:100%;text-align:right;font-size:12px;font-family:Times"><strong>Subtotal:</strong></td>
                            <td style="white-space:nowrap;padding-right:5px;height:20px;text-align:right;font-size:12px;font-family:Times"><span class="currency">${subtotal} USD</span></td>
                        </tr>
                        {shipping_html}
                        <tr>
                            <td height="4" colspan="2" style="font-size:12px;font-family:Times"></td>
                        </tr>
                        <tr>
                            <td style="padding-right:3px;height:25px;background:#cccccc none;width:100%;text-align:right;font-size:12px;font-family:Times"><strong>Total:</strong></td>
                            <td style="white-space:nowrap;padding-right:5px;height:25px;background:#cccccc none;text-align:right;font-size:12px;font-family:Times"><strong><span class="currency">${total} USD</span></strong></td>
                        </tr>
                    </table>
                </td>
            </tr>
                <tr>
                <td colspan="3" style="padding-top:10px;font-size:12px;font-family:Times">
                    <p style="font-size: 14px; font-weight: bold; text-align: center;">Quotation Conditions / Comments</p>
                    <div style="border: 1px solid #cecfce; padding: 5px; font-weight: 600; line-height: 1.5;">{additional_notes}<br />
        </div>
                </td>
            </tr> {wire_transfer}
            <hr />        <td><hr size="1" noshade="noshade" />
                </td>
            </tr>
            <tr>
                <td>
                <span>Prices are valid for 30 Days based on availability and total bill of material quoted. All fulfilled quotes will ship with insurance unless otherwise notified. This electronic message and any attachment contain confidential and privileged information belonging to the sender or intended recipient.
                    Please keep this information confidential. If you are not the intended recipient you are hereby notified that any
                    disclosure, copying, use, distribution, or taking of any action in reliance on the contents of this information is strictly prohibited.
                    If you have received this e-mail in error, please immediately notify me by reply email to sales@trwsupply.com
                    and delete all copies from your records. Product warranty is given in lieu of any other warranties, either express or implied, including that we disclaim any warranty of merchantability, fitness for a particular purpose and/or non-infringement. In no event shall we be liable for any damages except actual damages up to, but not exceeding, the amount paid to us for the product, including we shall not be liable for any consequential or indirect damages or lost profits whether or not advised of same. TRW Supply provided products are warranted for one full year unless otherwise stated.
            </span>
                </td>
            </tr>
        </table>
        </body>
        </html>
        """

        return html
    except Exception as e:
        print(e, "HTML")


def getViewHTMLText(
    parts_list,
    quantities_list,
    conditions_list,
    unit_totals_list,
    line_totals_list,
    stocks_list,
    sender,
    sender_email,
    quote_number,
    customer_email,
    subject,
    date,
    payment_method,
    delivery_method,
    additional_notes_list,
    isWireTransfer=False,
    shipping_charges="",
    customer_notes="",
):
    try:

        additional_notes = ""
        for note in additional_notes_list:
            if note == additional_notes_list[-1]:
                additional_notes += note
            else:
                additional_notes += note + "<br>"

        total = 0
        for dol in line_totals_list:
            if dol != "None" and dol != "":
                total += float(dol)
        total = "{:.2f}".format(total)
        subtotal = total

        parts_table = ""
        for i in range(len(parts_list)):
            parts_table += f"""<tr align = 'center'><td style='text-align: center;'>{i+1}</td><td style='text-align: center;'>{quantities_list[i]}</td><td style='text-align: left;'>{parts_list[i]}</td><td style='text-align: center;'>{conditions_list[i]}</td><td style = 'text-align: center;'>${unit_totals_list[i]}</td><td style='text-align: center;'>${line_totals_list[i]}</td><td style='text-align: center;'>{stocks_list[i]}</td></tr>"""

        if isWireTransfer:
            wire_transfer = wire_transfer_info
        else:
            wire_transfer = ""

        current_directory = str(os.path.dirname(os.path.realpath(__file__)))

        html = f"""
        <!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
        <html xmlns="http://www.w3.org/1999/xhtml">
        <head>
            <style type="text/css">
                BODY {{
                    MARGIN-TOP: 10px;
                    MARGIN-BOTTOM: 10px;
                    MARGIN-LEFT: 10px;
                    MARGIN-RIGHT: 10px;
                    FONT-SIZE: 12px;
                    FONT-FAMILY: Times;
                    PADDING: 0px;
                    BACKGROUND-COLOR: #FFFFFF;
                    COLOR: #000000;
                }}
                TD {{
                    FONT-SIZE: 12px;
                    FONT-FAMILY: Times;
                }}
                TH {{
                    FONT-SIZE: 13px;
                    FONT-FAMILY: Times;
                }}
                H1 {{
                    FONT-SIZE: 20px;
                }}
                TABLE,IMG,A {{
                    BORDER: 0px;
                    
                }}
                .templateButton{{
                    -moz-border-radius:3px;
                    -webkit-border-radius:3px;
                    /*@editable*/ background-color:#336699;
                    /*@editable*/ border:0;
                    border-collapse:separate !important;
                    border-radius:3px;
                }}
                /**
                * @tab Body
                * @section button style
                * @tip Set the styling for your email's button. Choose a style that draws attention.
                */
                .templateButton, .templateButton a:link, .templateButton a:visited, /* Yahoo! Mail Override */ .templateButton a .yshortcuts /* Yahoo! Mail Override */{{
                    /*@editable*/ color:#FFFFFF;
                    /*@editable*/ font-family:Arial;
                    /*@editable*/ font-size:15px;
                    /*@editable*/ font-weight:bold;
                    /*@editable*/ letter-spacing:-.5px;
                    /*@editable*/ line-height:100%;
                    text-align:center;
                    text-decoration:none;
                }}
            </style>
            <script type='text/javascript' src='{current_directory}/js/jquery/jquery-2.0.0.min.js'></script>
            <script type='text/javascript' src='{current_directory}/js/jquery/jquery-ui-1.10.3.custom.min.js'></script>
            <script type='text/javascript' src='{current_directory}/js/jquery/jquery-migrate-1.1.1.min.js'></script>
            <script type='text/javascript' src='{current_directory}/js/jquery/globalize.js'></script>
            <script type='text/javascript' src='{current_directory}/js/actions.js'></script>
            <!--<script type='text/javascript' src='js/plugins.js'></script>-->
        </head>
        <body style="font-size:12px;font-family:Times;background-color:#FFF;color:#000;margin:10px;padding:0">
        <script type="text/javascript">
            function sendQuoteEmail(qnum) {{
                //alert(qnum);
                $.post('mandrillReSendQuote.php', {{'sendQuote': qnum}}, function (data) {{
                    //alert(data);
                    returnValue = JSON.parse(data);
                    if (returnValue[0].status === "rejected") {{
                        $("#emailAlert").html('<div class="alert alert-error"><strong>Send Error! : ' + returnValue[0].email + '</strong> <br /> Reason: ' + returnValue[0].reject_reason + ' <br /> ID: ' + returnValue[0]._id + '</div>');
                        //document.getElementById('emailAlert').innerHTML = 'Fred Flinstone';
                    }} else {{
                        //$("#emailAlert").html(returnValue);
                        $("#emailAlert").html('<div class="alert alert-success"><strong>Quote Sent! : ' + returnValue[0].email + '</strong> <br /> Status: ' + returnValue[0].status + '<br /> Reason: ' + returnValue[0].reject_reason + ' <br /> ID: ' + returnValue[0]._id + '</div>');
                        //document.getElementById('emailAlert').innerHTML = 'Fred Flinstone  222222';
                    }}
                }});
            }}
        </script>
        <!-- BUTTONS ON TOP -->
        <span id="printMe" style="color:red; font-weight:900;"><br/>
                <FORM>
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" onclick="window.location.href = '/quoteEdit.php?load=82021-63603';" value="Edit Quote" />
                <!--<INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" value="" onclick="sendQuoteEmail('');" value="Resend Quote" />-->
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" onclick="window.location.href='mandrillReSendQuote.php?sendQuote=82021-63603'" value="E-Mail Quote" />
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none; value=" onClick="window.print()" value="Print View" />
                <INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none;" onClick="window.opener.location = 'logout.php';window.location.href = 'logout.php?close'" value="Exit" />
                <!--<INPUT TYPE="button" style="border:none;-webkit-box-shadow:none;box-shadow:none; value=" onClick="window.location.href = 'logout.php'" value="Done" />--> 
            </FORM>
             <div id="emailAlert" name="emailAlert"></div>
            </span>
        
        <table cellspacing="0" cellpadding="0"  style="max-width:960px;background-color:#ffffff;border:0; autosize:2.4;" summary="Order details">
                <tr>
                <td style="font-size:12px; font-family:Times; text-align: right;">
                    <table cellspacing="0" cellpadding="0"  style="width:100%;border:0" summary="Summary">
                        <tr>
                            <td style="vertical-align:top;font-size:12px;font-family:Times">
                                <div id="preview" style="width: 150px;height: 130px;color: #000;background-color: #fff;font-family: Georgia, serif;box-sizing: border-box;position: relative;overflow: hidden;font-size: 64px;"> <div class="element logo-text pre-test" id="sdew_1" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;background-color: rgba(0, 0, 0, 0);font-weight: 200;text-shadow: #333 2px 2px 2px;color: #446094;font-size: 45px;font-family: Georgia, serif;top: 2px;left: 18px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">TRW</p></div>
                                    <div class="element logo-text pre-test" id="sdew_2" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 25px;font-family: Georgia, serif;top: 40px;left: 10px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">ELECTRIC</p></div>
                                    <div class="element logo-text pre-test" id="sdew_3" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 26px;font-family: Georgia, serif;top: 60px;left: 41px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">AND</p></div>
                                    <div class="element logo-text pre-test" id="sdew_3" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 26px;font-family: Georgia, serif;top: 83px;left: 20px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">SUPPLY</p></div>
                                <div class="element logo-text pre-test" id="sdew_3" style="position: absolute;display: block;margin: 0;padding: 0;white-space: nowrap;text-shadow: #333 1px 1px 1px;color: #446094;font-size: 26px;font-family: Georgia, serif;top: 105px;left: 8px;"><p style="line-height: 1;margin: 0;padding: 0;text-rendering: optimizeLegibility;font-feature-settings: &quot;kern&quot;;-webkit-font-feature-settings: &quot;kern&quot;;-moz-font-feature-settings: &quot;kern=1&quot;;">COMPANY</p></div>
                                </div>
                            </td>
                            <td style="width:100%;padding-left:30px;font-size:12px;font-family:Times">
                                <table cellspacing="0" cellpadding="2" width="100%" summary="Details" style="border:0">
                                    <tr>
                                        <td valign="bottom" align="left" style="font-size:12px;font-family:Times">
                                            <p>                                        1106 Great Falls Ct. Unit A<br />
                                                Knightdale, NC 27545 USA<br />
                                                Tel: 1-800-479-8084<br />
                                                {sender}<br />
                                                Email: <a href="mailto:{sender_email}" style="border:0">{sender_email}<br /> <!-- CHANGE!! -->
                                                </a><a href="http://www.trwsupply.com">www.trwsupply.com</a><br />
                                            </p></td>
                                        <td valign="bottom"><strong  style="font-size: 20px; text-transform: uppercase;">
                                                Quotation # <span style="text-decoration: underline;">{quote_number}</span> </strong></td>
                                    </tr>
                                </table>
                            </td>
                        </tr>
                    </table>
                    <hr  style="border: 0px none; border-bottom: 2px solid #58595b; margin: 2px 0px 17px 0px; padding: 0px; height: 0px;"/>
                    <table cellspacing="0" cellpadding="5px" style="border:0;margin-bottom:15px; float:left; width:100%;" summary="Address">
                        <tr>
                            <td width="46%" align="left"><span style="font-size:14px; font-family:Times;"><strong>Customer Information</strong></span></td>
                            <td width="54%" align="left"><span style="font-size:14px; font-family:Times;padding-left:3px;"><strong> Quote Details</strong></span></td>
                        </tr>
                        <tr align="left">
                            <td width="18%" style="font-size:12px;font-family:Times;"><strong>Email: </strong>
                                {customer_email}                    </td>
                            <td style="font-size:12px;font-family:Times;padding-left: 8px;"><strong>Subject: </strong>
                                {subject}</td>
                        </tr>
                        <tr>
                            <td  align="left"></td>
                            <td><table border="0" style="width:100%;">
                                    <tr>
                                        <td width="174" align="left"><strong>Date:</strong></td>
                                                                        <td width="333" align="left">{date}</td>
                                    </tr>
                                    <tr>
                                        <td align="left"><strong>Payment  Method:</strong></td>
                                        <td align="left"><span>{payment_method}</span></td>
                                    </tr>
                                    <tr>
                                        <td width="174" align="left"><strong style="text-align: right">Delivery Method:</strong></td>
                                        <td width="333" align="left"><span>{delivery_method}</span></td>
                                    </tr>
                                    <!--<tr>
                                        <td width="174" align="left"><strong style="text-align: right">Total Shipping Weight:</strong></td>
                                                                        <td width="333" align="left"><span></span></td>
                                    </tr>-->
                                                            </table>
                            </td>
                        </tr>
                    </table>
                    <table cellspacing="0" cellpadding="3" width="100%" border="1" summary="Products" style="border:0">
                        <tr align="center">
                            <th width="2%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Item</th>
                            <th width="2%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Qty</th>
                            <th width="13%" nowrap="nowrap" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Part #</th>
                            <!--<th width="25%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Description</th>-->
                            <th width="8%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Condition</th>
                                                <th width="5%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Unit Price</th>
                            <th width="5%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Line Total</th>
                            <!--<th width="5%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Wt Ea.</th>-->
                            <th width="12%" bgcolor="#cccccc" style="font-size:13px;font-family:Times">Stock</th>
                        </tr>
                        {parts_table}
                    </table>
        <hr style="border: 0; border-bottom: 1px solid #000; background: #000;"/>
                    <table cellspacing="0" cellpadding="0" width="100%" border="0" id="html_order_info_total" summary="Total" style="border:0">
                        <tr>
                            <td height="4" colspan="2" style="font-size:12px;font-family:Times"></td>
                        </tr>
                        <tr>
                            <td style="padding-right:3px;height:20px;width:100%;text-align:right;font-size:12px;font-family:Times"><strong>Subtotal:</strong></td>
                            <td style="white-space:nowrap;padding-right:5px;height:20px;text-align:right;font-size:12px;font-family:Times"><span class="currency">${subtotal} USD</span></td>
                        </tr>
                        <tr>
                            <td height="4" colspan="2" style="font-size:12px;font-family:Times"></td>
                        </tr>
                        <tr>
                            <td style="padding-right:3px;height:25px;background:#cccccc none;width:100%;text-align:right;font-size:12px;font-family:Times"><strong>Total:</strong></td>
                            <td style="white-space:nowrap;padding-right:5px;height:25px;background:#cccccc none;text-align:right;font-size:12px;font-family:Times"><strong><span class="currency">${total} USD</span></strong></td>
                        </tr>
                    </table>
                </td>
            </tr>
                <tr>
                <td colspan="3" style="padding-top:10px;font-size:12px;font-family:Times">
                    <p style="font-size: 14px; font-weight: bold; text-align: center;">Quotation Conditions / Comments</p>
                    <div style="border: 1px solid #cecfce; padding: 5px; font-weight: 600; line-height: 1.5;">{additional_notes}<br />
        </div>
                </td>
            </tr>{wire_transfer}
            <hr />        <td><hr size="1" noshade="noshade" />
                </td>
            </tr>
            <tr>
                <td>
                <span>Prices are valid for 30 Days based on availability and <span style="font-weight: 900;">total bill of material quoted</span>. All fulfilled quotes will ship with insurance unless otherwise notified. This electronic message and any attachment contain confidential and privileged information belonging to the sender or intended recipient.
                    Please keep this information confidential. If you are not the intended recipient you are hereby notified that any
                    disclosure, copying, use, distribution, or taking of any action in reliance on the contents of this information is strictly prohibited.
                    If you have received this e-mail in error, please immediately notify me by reply email to sales@trwsupply.com
                    and delete all copies from your records. Product warranty is given in lieu of any other warranties, either express or implied, including that we disclaim any warranty of merchantability, fitness for a particular purpose and/or non-infringement. In no event shall we be liable for any damages except actual damages up to, but not exceeding, the amount paid to us for the product, including we shall not be liable for any consequential or indirect damages or lost profits whether or not advised of same. TRW Supply provided products are warranted for one full year unless otherwise stated.
            </span>
                </td>
            </tr>
        </table>
        </body>
        </html>
        """

        return html
    except Exception as e:
        print(e)


def makeQuotePDF(html, title):
    try:
        pdfkit.from_string(html, title + ".pdf", configuration=config)
        # pdfkit.from_string(html, title + '.pdf')
        pass
    except Exception as e:
        print(e)
