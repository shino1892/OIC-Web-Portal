FROM mysql:8.0

# 設定ファイルをコピー（任意でマウントでもOK）
COPY ./conf.d/my.cnf /etc/mysql/conf.d/my.cnf

# 起動時に権限を修正してから mysqld を起動する
ENTRYPOINT ["bash", "-c", "\
    chmod 644 /etc/mysql/conf.d/my.cnf && \
    chown root:root /etc/mysql/conf.d/my.cnf && \
    exec docker-entrypoint.sh mysqld \
"]