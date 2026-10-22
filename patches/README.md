# External trees and where the negroni changes live

negroni's changes are already tracked in this repository, so
there are no patch files to apply by hand yet:

| Tree | Baseline | negroni changes |
|---|---|---|
| XNU `xnu-8796.141.3` (CI builds it) | apple-oss-distributions/xnu | `negroni-ios/xnu/patches/*.patch` (applied in order by `.github/workflows/negroni-ios.yml`) |
| Mu-Silicium (`~/ios-work/Mu-Silicium`) | upstream Mu-Silicium | `uefi/negroni/negroniPkg` (synced into `Platforms/OnePlus/negroniPkg` by `uefi/negroni/shim-mu.sh`; `NegroniTouchDxe` has to be copied by hand) |
| UniXNU / DarwinBoot | built into the Mu-Silicium image | none for negroni yet |

When one of these needs a change that cannot live in this repository, put it here as
`<tree>-negroni.patch` with its baseline commit in this table.
