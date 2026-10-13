from pathlib import Path

import pandas as pd
import streamlit as st
from PIL import Image

from src.predict import (
    load_model_bundle,
    predict_image,
)


st.set_page_config(
    page_title="TrashBin Fill Monitor",
    page_icon="🗑️",
    layout="wide",
)


# ============================================================
# STYLE
# ============================================================

st.markdown(
    """
    <style>
        .block-container {
            padding-top: 2rem;
            padding-bottom: 3rem;
        }

        .main-title {
            font-size: 2.3rem;
            font-weight: 800;
            margin-bottom: 0.2rem;
        }

        .subtitle {
            color: #8b949e;
            margin-bottom: 1.5rem;
        }

        .result-box {
            border: 1px solid #30363d;
            border-radius: 14px;
            padding: 20px;
            margin-top: 10px;
        }

        .status-low {
            color: #3fb950;
            font-weight: 700;
        }

        .status-medium {
            color: #d29922;
            font-weight: 700;
        }

        .status-high {
            color: #f85149;
            font-weight: 700;
        }

        .small-note {
            color: #8b949e;
            font-size: 0.85rem;
        }
    </style>
    """,
    unsafe_allow_html=True,
)


# ============================================================
# MODEL
# ============================================================

@st.cache_resource
def get_model():
    return load_model_bundle()


try:
    bundle = get_model()

except Exception as exc:
    st.error(
        "Model gagal dimuat."
    )

    st.code(
        str(exc)
    )

    st.stop()


# ============================================================
# HEADER
# ============================================================

st.markdown(
    """
    <div class="main-title">
        🗑️ TrashBin Fill Monitor
    </div>

    <div class="subtitle">
        Computer Vision prototype untuk membantu
        memprioritaskan pengangkutan tempat sampah
        berdasarkan foto.
    </div>
    """,
    unsafe_allow_html=True,
)


st.info(
    """
    Prototype ini mengklasifikasikan gambar menjadi
    **empty**, **half-full**, atau **full**.

    Output digunakan sebagai bantuan prioritas pengangkutan,
    bukan sebagai pengganti verifikasi petugas.
    """
)


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:
    st.header(
        "Project Info"
    )

    st.write(
        "**Model:** MobileNetV3-Small"
    )

    st.write(
        "**Classes:**"
    )

    st.write(
        "• Empty\n"
        "• Half-full\n"
        "• Full"
    )

    st.divider()

    st.write(
        "**Device**"
    )

    st.code(
        str(bundle["device"])
    )

    if bundle.get(
        "validation_f1"
    ) is not None:

        st.metric(
            "Validation Macro-F1",
            f"{bundle['validation_f1']:.2%}",
        )

    st.divider()

    st.caption(
        """
        Training dilakukan pada simulated images.
        Real images digunakan sebagai external test.
        """
    )


# ============================================================
# UPLOAD
# ============================================================

uploaded_file = st.file_uploader(
    "Upload foto tempat sampah",
    type=[
        "jpg",
        "jpeg",
        "png",
        "webp",
    ],
)


if uploaded_file is None:
    st.subheader(
        "Cara menggunakan"
    )

    st.write(
        """
        1. Upload foto tempat sampah.
        2. Model melakukan klasifikasi level kepenuhan.
        3. Sistem menampilkan confidence.
        4. Sistem memberikan rekomendasi prioritas pengangkutan.
        """
    )

    st.warning(
        """
        Confidence model bukan persentase fisik volume sampah.

        Contoh: confidence 90% pada class FULL berarti model
        90% yakin bahwa gambar termasuk class FULL,
        bukan berarti tempat sampah terisi 90%.
        """
    )

    st.stop()


# ============================================================
# READ IMAGE
# ============================================================

image = Image.open(
    uploaded_file
).convert("RGB")


left_col, right_col = st.columns(
    [1.05, 1]
)


# ============================================================
# IMAGE PREVIEW
# ============================================================

with left_col:
    st.subheader(
        "Input Image"
    )

    st.image(
        image,
        use_container_width=True,
    )


# ============================================================
# PREDICTION
# ============================================================

result = predict_image(
    image=image,
    bundle=bundle,
)

label = result["label"]
confidence = result["confidence"]
priority = result["priority"]
probabilities = result["probabilities"]

status = priority["status"]
action = priority["action"]


# ============================================================
# RESULT PANEL
# ============================================================

with right_col:
    st.subheader(
        "Hasil Analisis"
    )

    label_display = (
        label
        .replace(
            "-",
            " ",
        )
        .title()
    )

    col1, col2 = st.columns(2)

    with col1:
        st.metric(
            "Prediksi",
            label_display,
        )

    with col2:
        st.metric(
            "Confidence",
            f"{confidence:.1%}",
        )

    if status == "HIGH":
        st.error(
            f"🔴 PRIORITY {status}"
        )

    elif status == "MEDIUM":
        st.warning(
            f"🟡 PRIORITY {status}"
        )

    else:
        st.success(
            f"🟢 PRIORITY {status}"
        )

    st.markdown(
        f"""
        ### Rekomendasi

        **{action}**
        """
    )

    st.caption(
        "Keputusan akhir tetap memerlukan verifikasi petugas."
    )


# ============================================================
# CLASS PROBABILITY
# ============================================================

st.divider()

st.subheader(
    "Probability Distribution"
)

prob_df = pd.DataFrame(
    {
        "Class": [
            k.replace(
                "-",
                " ",
            ).title()
            for k in probabilities.keys()
        ],
        "Probability": [
            v * 100
            for v in probabilities.values()
        ],
    }
)

prob_df = prob_df.sort_values(
    "Probability",
    ascending=False,
)

st.bar_chart(
    prob_df.set_index(
        "Class"
    )
)


prob_display = prob_df.copy()

prob_display[
    "Probability"
] = prob_display[
    "Probability"
].map(
    lambda x: f"{x:.2f}%"
)

st.dataframe(
    prob_display,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# OPERATIONAL INTERPRETATION
# ============================================================

st.divider()

st.subheader(
    "Interpretasi Operasional"
)

priority_table = pd.DataFrame(
    [
        {
            "Fill Level": "Empty",
            "Priority": "LOW",
            "Action": "Belum perlu diangkut",
        },
        {
            "Fill Level": "Half-full",
            "Priority": "MEDIUM",
            "Action": "Pantau / jadwalkan",
        },
        {
            "Fill Level": "Full",
            "Priority": "HIGH",
            "Action": "Prioritaskan pengangkutan",
        },
    ]
)

st.dataframe(
    priority_table,
    use_container_width=True,
    hide_index=True,
)


# ============================================================
# MODEL CONTEXT
# ============================================================

st.divider()

st.subheader(
    "Model Context"
)

metric1, metric2 = st.columns(
    2
)

with metric1:
    st.metric(
        "Simulated Validation Macro-F1",
        "83.08%",
    )

with metric2:
    st.metric(
        "Real External Test Macro-F1",
        "76.33%",
    )


st.caption(
    """
    Benchmark menggunakan akirsch1/waste-bin-dataset.

    Training dilakukan pada simulated images.
    Sebanyak 74 real images digunakan sebagai external
    domain-shift test.
    """
)


# ============================================================
# LIMITATIONS
# ============================================================

with st.expander(
    "Limitations"
):
    st.markdown(
        """
        - Mayoritas data training merupakan simulated images.
        - Real external test hanya terdiri dari 74 gambar.
        - Class FULL masih menjadi class paling sulit pada real test.
        - Confidence model bukan estimasi persentase volume fisik.
        - Sistem belum terhubung ke kamera atau sensor tempat sampah nyata.
        - Hasil model sebaiknya digunakan untuk membantu prioritas,
          bukan sebagai keputusan final.
        """
    )


st.divider()

st.caption(
    "TrashBin Fill Monitor — 5% AI/ML Portfolio Progress"
)