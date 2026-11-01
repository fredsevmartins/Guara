# Guara branding and repository name

The product and repository are named **Guara**, inspired by the Brazilian maned wolf mascot.
The owner completed the remote rename and the GitHub API confirmed `fredsevmartins/Guara`
with the original repository ID. Repository links and local remote configuration were updated.

The public Python and data interfaces remain compatible:

| Surface | Name |
| --- | --- |
| Product / repository / MCP server display name | Guara |
| Python distribution / executable | `opentruth` |
| Python import | `from opentruth import OpenTruth` |
| Default data directory | `.opentruth/` |
| Repository | `fredsevmartins/Guara` |

For existing checkouts, update the remote with:

```sh
git remote set-url origin https://github.com/fredsevmartins/Guara.git
```

Do not rename or move `.opentruth/`; no evidence migration is needed for the branding change.
The supplied DOI is retained. Check Zenodo's GitHub integration and repository metadata in the
DOI record separately; this session did not change the Zenodo record.
