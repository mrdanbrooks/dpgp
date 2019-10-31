# dgpg

``dgpg`` wraps gpg and vim to provide an encrypted file editor and viewer. 

It differs from the gnupg vim plugin in that rather than being vim and gpg specific, you can swap out vim for any other editor and gpg for any tool capable of symmetric encryption. 

## Dependencies

- gnupg (gpg)
- vim

## Installing

Simply download this git repo and run ``dgpg.py``.

Alternatively, you can add the following to your ``.bashrc`` file to make dgpg usable from anywhere on your system:

```bash
dgpg() {
   /path/to/dgpg.py "$@"
}
```

## Usage

To open an editor to create a new file called ``mysecrets.txt``:

```bash
$ dgpg mysecrets.txt
```

To edit an existing file file called ``mysecrets.txt`` (automatically decrypting and re-encrypting):

```bash
$ dgpg --edit mysecrets.txt
```

To view the decrypted contents of ``mysecrets.txt`` in a read only manner (using ``less``):

```bash
$ dgpg mysecrets.txt
```

