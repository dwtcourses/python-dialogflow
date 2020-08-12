# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""This script is used to synthesize generated parts of this library."""

import synthtool as s
from synthtool import gcp

gapic = gcp.GAPICBazel()

versions = ["v2beta1", "v2"]


for version in versions:
    library = gapic.py_library(
        "dialogflow",
        version,
        bazel_target=f"//google/cloud/dialogflow/{version}:dialogflow-{version}-py",
        include_protos=True,
    )

    s.move(
        library,
        excludes=[
            "google/**/*",
            "setup.py",
            "README.rst",
            "docs/index.rst",
            "docs/conf.py",
            "noxfile.py",
        ],
    )
    s.move(library / f"google/cloud/dialogflow_{version}", f"dialogflow_{version}")

    # Due to dialogflow being unique to the other google-cloud-* libraries,
    # a decent number of edits need to be done to correct naming and namespaces
    docs_paths = ["docs/**/*.rst", "docs/conf.py"]
    s.replace(docs_paths, "google-cloud-dialogflow", "dialogflow")
    s.replace(docs_paths, "google.cloud.dialogflow", "dialogflow")

    code_paths = ["tests/unit/gapic/**/*.py", f"dialogflow_{version}/**/*.py"]

    s.replace(code_paths, "import google.cloud.dialogflow", "import dialogflow")
    s.replace(code_paths, "from google.cloud\.", "from ")
    s.replace(code_paths, "from google.cloud import", "import")
    s.replace(code_paths, "google-cloud-dialogflow", "dialogflow")
    s.replace(code_paths, "'-dialogflow'", "'dialogflow'")
    s.replace(
        code_paths,
        "(Returns:\n\s+)([a-zA-Z]+Client:)",
        f"\g<1>dialogflow_{version}.\g<2>",
    )

    # Incorrectly formatted "raw" directive content block.
    s.replace(
        f"dialogflow_{version}/gapic/agents_client.py",
        "(\s+).. raw:: html\s+<pre>curl",
        "\g<1>.. raw:: html\g<1>    <pre>curl",
    )

# Some files are missing the appropriate utf-8 header
# -*- coding: utf-8 -*-
s.replace(
    [
        "dialogflow_v2beta1/proto/session_pb2.py",
        "dialogflow_v2beta1/proto/intent_pb2_grpc.py",
        "dialogflow_v2/proto/intent_pb2_grpc.py",
        "dialogflow_v2/proto/session_pb2.py",
    ],
    "# Generated by the .*",
    "# -*- coding: utf-8 -*-\n\g<0>",
)

s.replace(
    [
        "dialogflow_v2beta1/gapic/intents_client.py",
        "dialogflow_v2beta1/gapic/sessions_client.py",
        "dialogflow_v2/gapic/intents_client.py",
    ],
    "# Copyright 2018 Google LLC",
    "# -*- coding: utf-8 -*-\n\g<0>",
)

# Docstring has an extra '\' at the end of it '}\" \'
s.replace(
    "dialogflow_v2/gapic/agents_client.py",
    r"}\\\" [\\]\n(\s+retry \(Optional)",
    '}\\"\n\g<1>',
)

# Docstring has '-----' which is interpreted as RST section title
s.replace("dialogflow_v2beta1/proto/intent_pb2.py", "\s+-----------", "")

s.replace(
    "dialogflow_*/proto/session_pb2.py",
    "============================================================================",
    "",
)


# Replace bad hyperlink references
s.replace("dialogflow_*/proto/audio_config_pb2.py", "\s*\<\>`__", "`")


s.replace("dialogflow_v2/proto/agent_pb2.py", ":math:", "")
s.replace("dialogflow_v2/proto/agent_pb2.py", ":raw-latex:", "")

# ignore sphinx warnings
# TODO: remove with microgenerator transition
s.replace("noxfile.py",
"""['"]-W['"],  # warnings as errors""",
"")

s.shell.run(["nox", "-s", "blacken"], hide_output=False)
