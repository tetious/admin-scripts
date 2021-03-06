/// <reference path="typings/tsd.d.ts" />

// Simple node script intended to run under Lambda that takes an email ingested into S3 via SES and gives it a more useful name.
//
// This is free and unencumbered software released into the public domain.

var AWS = require('aws-sdk');
var s3 = new AWS.S3();

var bucketName = 'abs-mail-archive';

exports.handler = function (event, context) {

    var ses = JSON.parse(event.Records[0].Sns.Message);
    var date = new Date();
    var oldKey = 'tmp/' + ses.mail.messageId;
    var from = ses.mail.commonHeaders.from[0].replace(/[^\w@.<>]+/g, "_");
    var to = ses.mail.commonHeaders.to[0].replace(/[^\w@.<>]+/g, "_");
    var subject = ses.mail.commonHeaders.subject.replace(/\W+/g, "_").slice(0,30);

    var newKey = `${date.getFullYear() }/${date.getMonth() + 1}/${date.getDate() }/|${from}|${to}|${subject}|${ses.mail.messageId}.eml`;

    s3.copyObject({ Bucket: bucketName, CopySource: `${bucketName}/${oldKey}`, Key: newKey }, (err) => {
        if (err) {
            console.log("COPY ERROR:" + err, err.stack);
            context.fail();
        } else {
            s3.deleteObject({ Bucket: bucketName, Key: oldKey }, (err) => {
                if (err) {
                    console.log("DELETE ERROR:" + err, err.stack);
                    context.fail();
                }
                else {
                    console.log(`Copied email from <${from}> to ${newKey}`);
                    context.done();
                }
            })
        }
    });
};