import json
from typing import ClassVar, Dict, Optional
from urllib.parse import urljoin
from pathlib import Path

from jinja2.utils import markupsafe

from .settings import get_settings

settings = get_settings()


class JSLoader(object):
    """JS/Vite manifest loader"""

    instance = None
    manifest: ClassVar[dict]

    def __new__(cls):
        """Singleton manifest loader"""
        if cls.instance is not None:
            return cls.instance
        cls.manifest = {}
        cls.instance = super().__new__(cls)
        cls.instance.parse_manifest()

        return cls.instance

    def parse_manifest(self) -> None:
        """
        Read and parse the Vite manifest file.

        Raises:
            RuntimeError: if cannot load the file or JSON in file is malformed.
        """
        if settings.environment == "development":  # Dev is always HMR
            return

        manifest_path = Path(settings.static_url.removeprefix("/")) / "manifest.json"
        if not manifest_path.exists():
            raise RuntimeError(f"{manifest_path} not found")

        self.manifest = json.load(open(manifest_path, "r"))

    def generate_asset_server_url(self, path: Optional[str] = None) -> str:
        """
        Generates an URL to and asset served by the Vite development server.

        Keyword Arguments:
            path {Optional[str]} -- Path to the asset. (default: {None})

        Returns:
            str -- Full URL to the asset.
        """
        if settings.environment == "development":
            base_url = settings.dev_js_server

        else:
            base_url = settings.website_base_url

        return urljoin(
            base_url,
            urljoin(settings.static_url, path if path is not None else ""),
        )

    def generate_script_tag(self, src: str, attrs: Optional[Dict[str, str]] = None) -> str:
        """Generates an HTML script tag."""
        attrs_str = ""
        if attrs is not None:
            attrs_str = " ".join(
                ['{key}="{value}"'.format(key=key, value=value) for key, value in attrs.items()]
            )

        return f'<script {attrs_str} src="{src}"></script>'

    def generate_stylesheet_tag(self, href: str) -> str:
        """
        Generates and HTML <link> stylesheet tag for CSS.

        Arguments:
            href {str} -- CSS file URL.

        Returns:
            str -- CSS link tag.
        """
        return '<link rel="stylesheet" href="{href}" />'.format(href=href)

    def generate_js_asset(self, path: str, scripts_attrs: Optional[Dict[str, str]] = None) -> str:
        """
        Generates all assets include tags for the file in argument.

        Returns:
            str -- All tags to import this asset in yout HTML page.
        """
        if settings.environment == "development":
            return self.generate_script_tag(
                self.generate_asset_server_url(path),
                {"type": "module", "async": "", "defer": ""},
            )

        if path not in self.manifest:
            raise RuntimeError(f"Cannot find {path} in manifest")

        tags = []
        manifest_entry: dict = self.manifest[path]
        if not scripts_attrs:
            scripts_attrs = {"type": "module", "async": "", "defer": ""}

        # Add dependent CSS
        if "css" in manifest_entry:
            for css_path in manifest_entry.get("css"):
                tags.append(self.generate_stylesheet_tag(urljoin(settings.static_url, css_path)))

        # Add dependent "vendor"
        if "imports" in manifest_entry:
            for vendor_path in manifest_entry.get("imports"):
                tags.append(self.generate_js_asset(vendor_path, scripts_attrs=scripts_attrs))

        # Add the script by itself
        tags.append(
            self.generate_script_tag(
                urljoin(settings.static_url, manifest_entry["file"]),
                attrs=scripts_attrs,
            )
        )

        return "\n".join(tags)


def js_asset(asset_path: str, scripts_attrs: Optional[Dict[str, str]] = None) -> markupsafe.Markup:
    "Load JS asset"

    # if settings.environment == "development":
    #     base_url = settings.dev_js_server
    #     asset_file = asset_path

    # else:
    #     base_url = settings.website_base_url
    #     asset_file = get_file_from_manifest(asset_path)

    # s = f'<script type="module" src="{base_url}{settings.static_url}{asset_file}"></script>'

    # return markupsafe.Markup(s)
    return markupsafe.Markup(JSLoader().generate_js_asset(asset_path, scripts_attrs=scripts_attrs))


def js_dev_asset(
    asset_path: str, scripts_attrs: Optional[Dict[str, str]] = None
) -> markupsafe.Markup:
    "Load asset only if in dev mode."

    if settings.environment != "development":
        return markupsafe.Markup("")

    return js_asset(asset_path, scripts_attrs)
