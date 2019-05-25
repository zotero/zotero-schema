# Zotero Data Schema

This repo contains a schema file providing most of the information necessary for working with the Zotero data model. The file is served from the Zotero API at https://api.zotero.org/schema.

The schema file contains a JSON object with the following top-level properties:

  - `version`: The version number of the schema
  - `itemTypes`: A list of item types and their associated fields and creator types.
  - `meta`: Additional field info, such as which fields are date fields
  - `csl`: CSL type/field/creator mappings for converting between Zotero data and CSL JSON
  - `locales`: Localized strings for item types, fields, and creator types in all locales supported by Zotero

## Downloading the schema from your app

The schema file is large, so be sure your app’s HTTP client is passing `Accept-Encoding: gzip` with the download request. Cache the file along with its `ETag` header and, when checking for updates, make a conditional request using `If-None-Match: <ETag>`. In most cases, you will receive a `304` and should continue using the cached version.

## Bundling the schema file

To bundle the schema file in an app, copy schema.json and store the current schema.json.gz.etag as the ETag, which will allow your app to avoid redownloading the current version of the file when it first starts. Be sure to use `Accept-Encoding: gzip`, as the non-gzipped version has a different ETag.

## Checking for updates

In addition to regular (e.g., daily) conditional requests to check for updates, clients using the Zotero API can check the `Zotero-Schema-Version` response header for the current schema version. If the returned value is greater than the `version` property of the cached schema, clients should perform a schema update before continuing, as data returned from the API may include types or fields that have changed since the client’s schema version.
