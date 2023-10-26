from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

'''
def render_to_pdf(template_source, context_dict={}):
    template = get_template(template_source)
    html = template.render(context_dict)
    result = BytesIO()
    #pdf=pisa.pisaDocument(BytesIO(html.encode("ISO-8859-1")), result)
    pdf=pisa.pisaDocument(BytesIO(html.encode("cp1252")), result)  # ISO-8859-1
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type="application/pdf")
    return None
'''    