#!/bin/bash
set -x

MAIL="stephane.hamaili@gmail.com"


function exec(){
    PASSWD=$(gpg --decrypt ./.credentials/mail_passwd.gpg)
    TOKEN=$(gpg --decrypt ./.credentials/token.asc)

    export 'BEARER_TOKEN'=$TOKEN
    echo "Export of the token : Done"
    COMMAND=$(sudo git checkout main 2>&1)
    if [ $? -ne 0 ]
    then 
        echo "git checkout main : $COMMAND"
    else
        echo "\"sudo git checkout main\" command : Done"
        COMMAND=$(sudo git pull 2>&1)
        if [ $? -ne 0 ]
        then
            echo "git pull : $COMMAND"
        else
            echo "python"
            COMMAND=$(python3 twitter_request.py $PASSWD 2>&1)
            if [ $? -ne 0 ]
            then   
                echo "python3"
            fi
        fi
    fi
}

exec