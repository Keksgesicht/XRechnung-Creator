#!/usr/bin/env python

from datetime import datetime as DT
from datetime import timedelta
import xml.etree.cElementTree as ET
import xml.dom.minidom as MD
import XRechnung_config as cfg

output_file = "XRechnung_YYMMDD.xml"

### create XML

SE = ET.SubElement

namespaces = {
    "": "urn:oasis:names:specification:ubl:schema:xsd:Invoice-2",
    "cac": "urn:oasis:names:specification:ubl:schema:xsd:CommonAggregateComponents-2",
    "cec": "urn:oasis:names:specification:ubl:schema:xsd:CommonExtensionComponents-2",
    "cbc": "urn:oasis:names:specification:ubl:schema:xsd:CommonBasicComponents-2",
}


def ns_key(k):
    if k != "":
        return "xmlns:" + k
    else:
        return "xmlns"


def create_root():
    for prefix, uri in namespaces.items():
        ET.register_namespace(prefix, uri)
    root_ns_dict = {ns_key(k): v for k, v in namespaces.items()}
    root = ET.Element("Invoice", root_ns_dict)
    r_ci = SE(root, "cbc:CustomizationID")
    r_ci.text = "urn:cen.eu:en16931:2017#compliant#urn:xeinkauf.de:kosit:xrechnung_3.0"
    r_pi = SE(root, "cbc:ProfileID")
    r_pi.text = "urn:fdc:peppol.eu:2017:poacc:billing:01:1.0"
    r_id = SE(root, "cbc:ID")
    r_id.text = time_now_yymmdd
    r_issd = SE(root, "cbc:IssueDate")
    r_issd.text = time_now_longdate
    r_due = SE(root, "cbc:DueDate")
    r_due.text = time_due_longdate
    r_itc = SE(root, "cbc:InvoiceTypeCode")
    r_itc.text = "380"
    r_dcc = SE(root, "cbc:DocumentCurrencyCode")
    r_dcc.text = "EUR"
    r_br = SE(root, "cbc:BuyerReference")
    r_br.text = cfg.CUSTOMER_LEIT_ID
    r_ip = SE(root, "cac:InvoicePeriod")
    r_ip_sd = SE(r_ip, "cbc:StartDate")
    r_ip_sd.text = time_start
    r_ip_ed = SE(r_ip, "cbc:EndDate")
    r_ip_ed.text = time_end

    return root


def supplier_data(root):
    t_asp = SE(root, "cac:AccountingSupplierParty")
    t_pt = SE(t_asp, "cac:Party")

    t_eID = SE(t_pt, "cbc:EndpointID", {"schemeID": "EM"})
    t_eID.text = cfg.SUPPLIER_MAIL
    t_pname = SE(t_pt, "cac:PartyName")
    t_name = SE(t_pname, "cbc:Name")
    t_name.text = cfg.SUPPLIER_NAME_COMPANY

    t_addr = SE(t_pt, "cac:PostalAddress")
    t_pa_sn = SE(t_addr, "cbc:StreetName")
    t_pa_sn.text = cfg.SUPPLIER_ADDR_STREET
    t_pa_cn = SE(t_addr, "cbc:CityName")
    t_pa_cn.text = cfg.SUPPLIER_ADDR_CITY
    t_pa_pz = SE(t_addr, "cbc:PostalZone")
    t_pa_pz.text = cfg.SUPPLIER_ADDR_ZIP
    t_pa_c = SE(t_addr, "cac:Country")
    t_pa_idc = SE(t_pa_c, "cbc:IdentificationCode")
    t_pa_idc.text = "DE"

    t_tax = SE(t_pt, "cac:PartyTaxScheme")
    t_tax_cID = SE(t_tax, "cbc:CompanyID")
    t_tax_cID.text = cfg.SUPPLIER_TAX_UST
    t_tax_scheme = SE(t_tax, "cac:TaxScheme")
    t_tax_scheme_id = SE(t_tax_scheme, "cbc:ID")
    t_tax_scheme_id.text = "VAT"

    t_tax = SE(t_pt, "cac:PartyTaxScheme")
    t_tax_cID = SE(t_tax, "cbc:CompanyID")
    t_tax_cID.text = cfg.SUPPLIER_TAX_ID
    t_tax_scheme = SE(t_tax, "cac:TaxScheme")
    t_tax_scheme_id = SE(t_tax_scheme, "cbc:ID")
    t_tax_scheme_id.text = "FC"

    t_ple = SE(t_pt, "cac:PartyLegalEntity")
    t_ple_rn = SE(t_ple, "cbc:RegistrationName")
    t_ple_rn.text = cfg.SUPPLIER_NAME_COMPANY

    t_con = SE(t_pt, "cac:Contact")
    t_con_name = SE(t_con, "cbc:Name")
    t_con_name.text = cfg.SUPPLIER_NAME_PERSON
    t_con_tel = SE(t_con, "cbc:Telephone")
    t_con_tel.text = cfg.SUPPLIER_TEL
    t_con_mail = SE(t_con, "cbc:ElectronicMail")
    t_con_mail.text = cfg.SUPPLIER_MAIL

    return root


def customer_data(root):
    t_asp = SE(root, "cac:AccountingCustomerParty")
    t_pt = SE(t_asp, "cac:Party")

    t_eID = SE(t_pt, "cbc:EndpointID", {"schemeID": "EM"})
    t_eID.text = cfg.CUSTOMER_MAIL
    t_pname = SE(t_pt, "cac:PartyName")
    t_name = SE(t_pname, "cbc:Name")
    t_name.text = cfg.CUSTOMER_NAME

    t_addr = SE(t_pt, "cac:PostalAddress")
    t_pa_sn = SE(t_addr, "cbc:StreetName")
    t_pa_sn.text = cfg.CUSTOMER_ADDR_STREET
    t_pa_cn = SE(t_addr, "cbc:CityName")
    t_pa_cn.text = cfg.CUSTOMER_ADDR_CITY
    t_pa_pz = SE(t_addr, "cbc:PostalZone")
    t_pa_pz.text = cfg.CUSTOMER_ADDR_ZIP
    t_pa_c = SE(t_addr, "cac:Country")
    t_pa_idc = SE(t_pa_c, "cbc:IdentificationCode")
    t_pa_idc.text = "DE"

    t_ple = SE(t_pt, "cac:PartyLegalEntity")
    t_ple_rn = SE(t_ple, "cbc:RegistrationName")
    t_ple_rn.text = cfg.CUSTOMER_NAME

    return root


def payment_data(root):
    t_pay = SE(root, "cac:PaymentMeans")
    t_pay_code = SE(t_pay, "cbc:PaymentMeansCode")
    t_pay_code.text = "58"
    t_pay_id = SE(t_pay, "cbc:PaymentID")
    t_pay_id.text = cfg.CUSTOMER_PAY_PREFIX + " " + time_now_yymmdd
    t_pay_fa = SE(t_pay, "cac:PayeeFinancialAccount")
    t_pay_fa_id = SE(t_pay_fa, "cbc:ID")
    t_pay_fa_id.text = cfg.SUPPLIER_BANK_IBAN
    t_pay_fa_name = SE(t_pay_fa, "cbc:Name")
    t_pay_fa_name.text = cfg.SUPPLIER_NAME_PERSON
    t_pay_fa_fib = SE(t_pay_fa, "cac:FinancialInstitutionBranch")
    t_pay_fa_bic = SE(t_pay_fa_fib, "cbc:ID")
    t_pay_fa_bic.text = cfg.SUPPLIER_BANK_BIC
    return root


def invoice_total(root):
    AMOUNT_TOTAL = 0
    for pos_date, pos_hur in cfg.INVOICE_HUR_LINES.items():
        AMOUNT_TOTAL += cfg.INVOICE_HUR_FACTOR * pos_hur
    AMOUNT_PAY = AMOUNT_TOTAL - cfg.INVOICE_ALREADY_PAYED

    t_tax = SE(root, "cac:TaxTotal")
    t_tax_amount = SE(t_tax, "cbc:TaxAmount", {"currencyID": "EUR"})
    t_tax_amount.text = str(0.00)  # §19 (1) UStG
    t_ts = SE(t_tax, "cac:TaxSubtotal")
    t_ts_a_able = SE(t_ts, "cbc:TaxableAmount", {"currencyID": "EUR"})
    t_ts_a_able.text = str(AMOUNT_TOTAL)
    t_ts_a = SE(t_ts, "cbc:TaxAmount", {"currencyID": "EUR"})
    t_ts_a.text = str(0.00)  # §19 (1) UStG
    t_ts_tc = SE(t_ts, "cac:TaxCategory")
    t_ts_id = SE(t_ts_tc, "cbc:ID")
    t_ts_id.text = "Z"
    t_ts_id = SE(t_ts_tc, "cbc:Percent")
    t_ts_id.text = str(0)  # §19 (1) UStG
    t_ts_sch = SE(t_ts_tc, "cac:TaxScheme")
    t_ts_sch_id = SE(t_ts_sch, "cbc:ID")
    t_ts_sch_id.text = "VAT"

    t_lmt = SE(root, "cac:LegalMonetaryTotal")
    t_lea = SE(t_lmt, "cbc:LineExtensionAmount", {"currencyID": "EUR"})
    t_lea.text = str(AMOUNT_TOTAL)
    t_tea = SE(t_lmt, "cbc:TaxExclusiveAmount", {"currencyID": "EUR"})
    t_tea.text = str(AMOUNT_TOTAL)
    t_tia = SE(t_lmt, "cbc:TaxInclusiveAmount", {"currencyID": "EUR"})
    t_tia.text = str(AMOUNT_TOTAL)
    t_ata = SE(t_lmt, "cbc:AllowanceTotalAmount", {"currencyID": "EUR"})
    t_ata.text = str(0.00)
    t_prea = SE(t_lmt, "cbc:PrepaidAmount", {"currencyID": "EUR"})
    t_prea.text = str(cfg.INVOICE_ALREADY_PAYED)
    t_prea = SE(t_lmt, "cbc:PayableAmount", {"currencyID": "EUR"})
    t_prea.text = str(AMOUNT_PAY)

    return root


def invoice_line(pos_id, pos_date, pos_hur):
    t_il = ET.Element("cac:InvoiceLine")
    t_il_id = SE(t_il, "cbc:ID")
    t_il_id.text = str(pos_id)
    t_il_iq = SE(t_il, "cbc:InvoicedQuantity", {"unitCode": "HUR"})
    t_il_iq.text = str(pos_hur)
    t_il_lea = SE(t_il, "cbc:LineExtensionAmount", {"currencyID": "EUR"})
    t_il_lea.text = str(cfg.INVOICE_HUR_FACTOR * pos_hur)
    t_item = SE(t_il, "cac:Item")
    t_desc = SE(t_item, "cbc:Description")
    t_desc.text = pos_date
    t_item_name = SE(t_item, "cbc:Name")
    t_item_name.text = cfg.INVOICE_NAME
    t_sii = SE(t_item, "cac:SellersItemIdentification")
    t_sii_id = SE(t_sii, "cbc:ID")
    t_sii_id.text = str(pos_id)
    t_ctc = SE(t_item, "cac:ClassifiedTaxCategory")
    t_ctc_id = SE(t_ctc, "cbc:ID")
    t_ctc_id.text = "Z"
    t_ctc_pct = SE(t_ctc, "cbc:Percent")
    t_ctc_pct.text = str(0)  # §19 (1) UStG
    t_ctc_sch = SE(t_ctc, "cac:TaxScheme")
    t_ctc_sch_id = SE(t_ctc_sch, "cbc:ID")
    t_ctc_sch_id.text = "VAT"
    t_hur_price = SE(t_il, "cac:Price")
    t_hur_price_amount = SE(t_hur_price, "cbc:PriceAmount", {"currencyID": "EUR"})
    t_hur_price_amount.text = str(cfg.INVOICE_HUR_FACTOR)
    return t_il


def invoice_data(root):
    root = invoice_total(root)
    pos_id = 1
    for pos_date, pos_hur in cfg.INVOICE_HUR_LINES.items():
        t_il = invoice_line(pos_id, pos_date, pos_hur)
        root.append(t_il)
        pos_id += 1

    return root


def invoice_time(date_str):
    time_se = DT.strptime(date_str, "%d.%m.%y")
    return time_se.strftime("%Y-%m-%d")


def save_xml(root, file_path):
    # xml_declaration = '<?xml version="1.0" encoding="UTF-8"?>\n'
    xml_str = ET.tostring(root, encoding="UTF-8", xml_declaration=True)
    parsed_xml = MD.parseString(xml_str)
    pretty_xml = parsed_xml.toprettyxml(indent="  ")
    with open(file_path, "w", encoding="UTF-8") as f:
        # f.write(xml_declaration + pretty_xml)
        f.write(pretty_xml)


time_now = DT.now()
time_due = time_now + timedelta(days=30)

time_start = invoice_time(list(cfg.INVOICE_HUR_LINES.keys())[0])
time_end = invoice_time(list(cfg.INVOICE_HUR_LINES.keys())[-1])

time_now_yymmdd = time_now.strftime("%y%m%d")
time_now_longdate = time_now.strftime("%Y-%m-%d")
time_due_longdate = time_due.strftime("%Y-%m-%d")

root = create_root()
root = supplier_data(root)
root = customer_data(root)
root = payment_data(root)
root = invoice_data(root)

output_file = "XRechnung_" + time_now_yymmdd + ".xml"
save_xml(root, output_file)
print(f"Extended XML file saved as {output_file}")
