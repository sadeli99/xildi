const crypto = require('crypto');
const base64 = require('base64-js');
const JSON = require('json-bigint');

class CryptoJsAes {
    static encrypt(value, passphrase) {
        const salt = crypto.randomBytes(8);
        let salted = Buffer.alloc(0);
        let dx = Buffer.alloc(0);
        while (salted.length < 48) {
            dx = crypto.createHash('md5').update(dx.toString('binary') + passphrase + salt.toString('binary')).digest();
            salted = Buffer.concat([salted, dx]);
        }
        const key = salted.slice(0, 32);
        const iv = salted.slice(32, 48);

        const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
        const encryptedData = Buffer.concat([cipher.update(JSON.stringify(value), 'utf8'), cipher.final()]);

        return JSON.stringify({
            ct: base64.fromByteArray(encryptedData).toString('utf-8'),
            iv: iv.toString('hex'),
            s: salt.toString('hex')
        });
    }

    static decrypt(jsonStr, passphrase) {
        const jsonData = JSON.parse(jsonStr);
        const salt = Buffer.from(jsonData.s, 'hex');
        const iv = Buffer.from(jsonData.iv, 'hex');
        const ct = base64.toByteArray(jsonData.ct);

        const concatedPassphrase = Buffer.concat([Buffer.from(passphrase, 'utf-8'), salt]);
        let result = crypto.createHash('md5').update(concatedPassphrase).digest();
        for (let i = 1; i < 3; i++) {
            result = crypto.createHash('md5').update(result + concatedPassphrase.toString('binary')).digest();
        }
        const key = result.slice(0, 32);

        const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
        let decryptedData = Buffer.concat([decipher.update(ct), decipher.final()]);

        try {
            return JSON.parse(CryptoJsAes._unpad(decryptedData).toString('utf-8'));
        } catch (e) {
            console.error(`Error decoding JSON: ${e}`);
            return null;
        }
    }

    static _pad(s) {
        const padding = 16 - (s.length % 16);
        return Buffer.concat([s, Buffer.alloc(padding, padding)]);
    }

    static _unpad(s) {
        const padding = s[s.length - 1];
        return s.slice(0, s.length - padding);
    }
}

module.exports = CryptoJsAes;
