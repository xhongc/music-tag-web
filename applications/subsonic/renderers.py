import collections
import xml.etree.ElementTree as ET

from rest_framework import renderers



# from https://stackoverflow.com/a/8915039
# because I want to avoid a lxml dependency just for outputting cdata properly
# in a RSS feed
def CDATA(text=None):
    element = ET.Element("![CDATA[")
    element.text = text
    return element


ET._original_serialize_xml = ET._serialize_xml


def _serialize_xml(write, elem, qnames, namespaces, **kwargs):
    if elem.tag == "![CDATA[":
        write(f"<{elem.tag}{elem.text}]]>")
        return
    return ET._original_serialize_xml(write, elem, qnames, namespaces, **kwargs)


ET._serialize_xml = ET._serialize["xml"] = _serialize_xml
# end of tweaks


def structure_payload(data):
    payload = {
        "MusicTagVersion": "1",
        "status": "ok",
        "type": "music-tag",
        "version": "1.16.0",
    }
    payload.update(data)
    if "detail" in payload:
        payload["error"] = {"code": 0, "message": payload.pop("detail")}
    if "error" in payload:
        payload["status"] = "failed"
    return collections.OrderedDict(sorted(payload.items(), key=lambda v: v[0]))


class SubsonicJSONRenderer(renderers.JSONRenderer):
    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = {"subsonic-response": structure_payload(data)}
        return super().render(final, accepted_media_type, renderer_context)


class SubsonicXMLRenderer(renderers.JSONRenderer):
    media_type = "text/xml"

    def render(self, data, accepted_media_type=None, renderer_context=None):
        if not data:
            # when stream view is called, we don't have any data
            return super().render(data, accepted_media_type, renderer_context)
        final = structure_payload(data)
        final["xmlns"] = "http://subsonic.org/restapi"
        tree = dict_to_xml_tree("subsonic-response", final)
        return b'<?xml version="1.0" encoding="UTF-8"?>\n' + ET.tostring(
            tree, encoding="utf-8"
        )


def dict_to_xml_tree(root_tag, d, parent=None):
    root = ET.Element(root_tag)
    for key, value in d.items():
        if isinstance(value, dict):
            root.append(dict_to_xml_tree(key, value, parent=root))
        elif isinstance(value, list):
            for obj in value:
                if isinstance(obj, dict):
                    el = dict_to_xml_tree(key, obj, parent=root)
                else:
                    el = ET.Element(key)
                    el.text = str(obj)
                root.append(el)
        else:
            if key == "value":
                root.text = str(value)
            elif key == "cdata_value":
                root.append(CDATA(value))
            else:
                root.set(key, str(value))
    return root
