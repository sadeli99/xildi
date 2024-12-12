const crypto = require('crypto');
const base64 = require('base64-js');

class CryptoJsAes {
    static encrypt(value, passphrase) {
        const salt = crypto.randomBytes(8);  // Generate a random salt (8 bytes)
        let salted = Buffer.alloc(0);
        let dx = Buffer.alloc(0);
        
        // Repeat the process to get 48 bytes of salted data
        while (salted.length < 48) {
            dx = crypto.createHash('md5').update(dx + passphrase + salt.toString('utf-8')).digest();
            salted = Buffer.concat([salted, dx]);
        }
        
        const key = salted.slice(0, 32);  // First 32 bytes as key
        const iv = salted.slice(32, 48);  // Next 16 bytes as iv (initialization vector)

        const cipher = crypto.createCipheriv('aes-256-cbc', key, iv);
        let encryptedData = cipher.update(JSON.stringify(value), 'utf8', 'base64');
        encryptedData += cipher.final('base64');

        return JSON.stringify({
            ct: encryptedData,
            iv: iv.toString('hex'),
            s: salt.toString('hex')
        });
    }

    static decrypt(jsonStr, passphrase) {
        const jsonData = JSON.parse(jsonStr);
        const salt = Buffer.from(jsonData.s, 'hex');  // Convert salt from hex
        const iv = Buffer.from(jsonData.iv, 'hex');  // Convert iv from hex
        const ct = base64.toByteArray(jsonData.ct);  // Convert cipher text from base64

        // Generate key using passphrase and salt
        const concatenatedPassphrase = Buffer.concat([Buffer.from(passphrase), salt]);
        let result = crypto.createHash('md5').update(concatenatedPassphrase).digest();

        for (let i = 0; i < 2; i++) {
            result = crypto.createHash('md5').update(result + concatenatedPassphrase.toString('utf-8')).digest();
        }

        const key = result.slice(0, 32);  // First 32 bytes as the encryption key

        // Decrypt the cipher text
        const decipher = crypto.createDecipheriv('aes-256-cbc', key, iv);
        let decryptedData = decipher.update(ct);
        decryptedData = Buffer.concat([decryptedData, decipher.final()]);

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
        return s.slice(0, s.length - s[s.length - 1]);
    }
}

module.exports = CryptoJsAes;
