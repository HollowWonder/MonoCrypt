FROM    python:3.13.11
LABEL   maintainer = "HollowWonder" \
        source = "https://github.com/HollowWonder/MonoCrypt.git"
WORKDIR /app
COPY    . .
RUN     pip install --upgrade --root-user-action=ignore pip && \
        pip install --root-user-action=ignore -r requirements.txt
