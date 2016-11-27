
**Requirements:

Testing:
WebTest
pyhamcrest
webapp2
jinja2


make virtual env:
add2virtualenv (base project directory)
add2virtualenv (~/google-cloud-sdk/platform/google_appengine/)
add2virtualenv (~/google-cloud-sdk/platform/google_appengine/lib/yaml/lib)

gcloud beta emulators datastore start
gcloud beta emulators datastore env-init
DATASTORE_USE_PROJECT_ID_AS_APP_ID=true