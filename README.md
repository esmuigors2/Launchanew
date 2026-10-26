# launchanew

A Bash wrapper for running batches of **Gaussian** (g98 / g03 / g09 / g16) jobs. It restarts failed jobs, launches additional utilities between jobs, and tries to fix common failures automatically (SCF and geometry convergence, numeric integration, `Opt=CalcAll` issues, saddle points, SC-PCM problems, and more).

Current version: **0.9.0.5.1**

```
Usage: launchanew [OPTIONS] /path/to/inputfile.gjf [/path/to/outputfile.out] [&> /path/to/logfile.logg] &
```

## What it does

- Every failure is reported to stdout and to `$HOME/CalcLog.logg.$HOSTNAME`.
- Inputs of failed jobs are copied to `/path/to/inputfile_failed.gjf`.
- At the end, all `.out` and `.fchk` files are compressed to `/path/to/inputfile.tgz` and `/path/to/inputfile_fchks.tgz` (use `-Z` to skip archiving the output).
- If the output file name is not given, the input file name is used with `.gjf` replaced by `.out`.
- The script refuses to start if the output file already exists.

Options can be combined in bulk, e.g. `launchanew -crom input.file`.

## Requirements

Also available via `launchanew -q`.

1. `perl`, `sed`, `awk` (and `gawk`); plus `python` if you want to use the problem solver. It was used since the computational cluster had fairly old versions of these tools.
2. A working Gaussian installation with these environment variables set:
   - `GAUSS_EXEDIR`: must point to a `g98`, `g03`, `g09` or `g16` directory, which must also be in `PATH`
   - `GAUSS_SCRDIR`: main scratch directory (required)
   - `GAUSS_SPRSCRDIR`, `GAUSS_SPRSCRDIR2`: additional scratch directories (optional)
   - `GAUSS_LNCHDIR`: directory usually containing input, output and checkpoint files (optional fallback; defaults to the current directory)
3. The companion library `~/bin/liblaunchanew.2026.10.26`. The script exits if it cannot be loaded.
4. External helper scripts on your `$PATH`: `doloiduraka`, `linda2gjf`, `monitram`, `proc2gjf`, `rwf2gjf`, `sarakstu1`, `sos_save`. The library also uses `anfreqevery`, `findminstep`, `findmingeom`, `sarakstu2` and `shift_coords.py`.
5. The shebang is `#!/home/igors/bin/bashx` which is just bash but makes the shell to read the script as a whole. This is handy for updates without interrupting the calculations already running.

Add to your `~/.bashrc` or `~/.bash_profile`:

```bash
GAUSS_LNCHDIR=/path/to/directory/with/input/output/and/chk/files   # optional fallback
GAUSS_SPRSCRDIR=/path/to/additional/scratch/directory              # optional
export GAUSS_SPRSCRDIR GAUSS_LNCHDIR
```

## Input file conventions

Input files are encouraged (**but not always required**) to have a title section of the form:

```
::: input_geometry_filename output_geometry_filename job_group_name job_processing_sub_name multistep_job_name job_step_in_multistep_job
```

- Input and output geometry names should match unless the job is an optimization.
- Job results are extracted automatically and stored in spreadsheet files (one per compound). `job_group_name` is the sheet name inside such a file.
- `multistep_job_name` is the name of a compound job, which is useful for grouping jobs in a batch file. For example, `Ionization` has three steps (neutral, cation, anion), and `ExcitedStateAbsorption` has a single point that stores the slow component of the reaction field, followed by the TD calculation.
- `job_step_in_multistep_job` is an integer from 1 to 9.
- **For `launchanew` to work fully**, you only need to set `multistep_job_name` and `job_step_in_multistep_job` in each title section (see `-c` and `-d` for why). Example: `::: a b c d e 1`
- The first step of a geometry optimization is recognized by matching `GeometryOptimization 1`. Edit the script if you use other names.
- Jobs that should not be archived (fragmented or other sophisticated guesses, jobs producing natural orbitals, etc.) can be marked by setting both geometry names to `0000_000 0000_000` (see `-z`).
- If the route section uses `/Gen`, the input must contain a `!==GENBASISSET== YOUR_BASIS_NAME` comment line. The script prints an error and a `sed` one-liner to add it.

### `!lutil` commands (optional)

Gaussian comment lines starting with `!lutil` are executed as bash commands between jobs. Typical uses are splitting large batch jobs so output files are easier to process, or producing formatted checkpoint files during a batch:

```
!lutil echo 'Splitting..'
!lutil formchk -3 chk_name.chk
```

Everything after `!lutil` is run as a bash command. When one is encountered, the input file is split into parts named `file_U1.gjf`, `file_U2.gjf`, and so on. If you don't use them, the script works fine.

## Forceful termination

To terminate a job on purpose (for example, to restart an optimization from a selected geometry):

1. Modify the next full sub-GJF file so that it starts with the tasks you want to launch instead of the currently running one. If `aa_U2_1_2_5.gjf` is running, modify `aa_U3.gjf`.
2. Delete all contents of the currently used sub-GJF file (here, `aa_U2_1_2_5.gjf`).
3. Kill the active Gaussian link (see `top` or `ps aux | grep $USER`).

The script tidies up after the kill and starts your desired jobs.

## Options

Options that take a value are shown with `ARG`.

### Scratch directory cleanup (`$GAUSS_SCRDIR`)

By default, scratch files are deleted once before start and after every misrun of Gaussian.

| Option | Description |
|--------|-------------|
| `-r`, `--remove` | Do **not** clean the scratch directory once at the beginning. |
| `-a`, `--noalltimeneat` | Do **not** clean it after every misrun of Gaussian. |

### Jobs using checkpoint files modified by failed jobs

| Option | Description |
|--------|-------------|
| *(none)* | All jobs until the end of the compound job are omitted. A compound job contains multiple steps that are all needed for complete results. |
| `-c`, `--ccheck` | Only the job using the CHK from the job that just failed is omitted. |
| `-d`, `--nodscheck` | Do **not** remove even the remaining steps of the failed multistep job that used the CHK. |
| `-o`, `--useoldchk` | Continue from the previous CHK file without foolproofing. By default, `launchanew` aborts if any `.chk` file mentioned in the input is already in the present directory. |
| `-n`, `--monitorchk` | For debugging: output the list of CHK files in the working directory after each sub-GJF completes. |
| `-C ARCHIVE`, `--getchks ARCHIVE` | Read CHK files for the present calculations from `ARCHIVE` (tar or 7z). Implies `-o`. |
| `-f`, `--preservechk` | Do not delete checkpoint files at the end. By default they are deleted; use `formchk` or `cp` in the `!lutil` section if you want to keep orbitals, etc. |

### Automatic solution of computational problems

| Option | Description |
|--------|-------------|
| `-j`, `--gofiner` | Try to solve numeric integration problems by adopting a finer grid. This may cause problems when comparing with other results. |
| `-s`, `--notrysolve` | Do **not** try to solve SCF convergence, integration, Opt or Polar problems (for example, switching off FMM when necessary). |
| `-F`, `--nocalcall` | Do **not** try to solve optimization problems by adding `CalcAll` with the current model chemistry. |

If `-s` is **not** set, these options are also considered:

| Option | Description |
|--------|-------------|
| `-e ARG`, `--calcfcevery ARG` | Include calculation of method-specific force constants every `ARG` steps (default 20). This may reduce the computational cost. |
| `-b`, `--banginghead` | Also try to solve SCF convergence problems with solutions that might not work at all (if you are desperate). |
| `-g`, `--shsaddle` | Do **not** try to solve the problem of reaching a saddle point instead of a minimum in a geometry optimization (normally done by shifting the geometry along normal modes with negative force constants). |

### Input modification and resources

| Option | Description |
|--------|-------------|
| `-i`, `--changedir` | Substitute all paths in the input file with the current directory. |
| `-x`, `--nomaxdisk` | Remove the `MaxDisk` keyword from the route line (this allows using all the space in the last scratch directory without a size limit, or `-1`). |
| `-w`, `--norwfmod` | Do not modify the size of RWF files according to the disk available on the node (useful if you already determined an optimal RWF size). |
| `-l "node1,node2,..."`, `--addlinda "node1,node2,..."` | Add or modify the `%LindaWorkers` directive in the GJF file. |
| `-p N`, `--noprocmod=N` | Use only `N` CPU cores for this job. If `N=0`, memory and CPU core count are not modified at all (useful if you already determined optimal values). For finer control, see `proc2gjf -h`. |

### Output handling and job control

| Option | Description |
|--------|-------------|
| `-z`, `--okzero` | Do **not** remove, after the calculation, jobs whose title section starts with `::: 0000_000 0000_000`. These jobs are typically used to generate `.FCHK` files with relevant data (NO, NTO, etc.). |
| `-u`, `--nostupid` | Delete the output file if it contains no `Normal termination` or a functional lacked abilities for a compound job. |
| `-y`, `--neverstop` | Do not stop batch execution after many consecutive errors (used, for example, for manual PES scans from autogenerated geometries that include overlapping atoms). |
| `-I ARG`, `--nintersperse=ARG` | To prevent long file names when erroring, the file is split by a dummy `!lutil` command when the distance between `!lutil` lines exceeds `ARG` jobs. Done by default with `ARG=10`. |
| `-k`, `--nodalek` | Make the job immune to the *dalek*, a script that runs constantly and checks every 60 minutes for hung scripts across the cluster. |
| `-m`, `--monram` | Monitor RAM usage every 5 minutes, writing to `$HOME/MemLog.<hostname>.logg` and `$HOME/DiskLog.<hostname>`. |
| `-Z`, `--notar` | Do not archive the output file (useful for external scripts). |

### Help and diagnostics

| Option | Description |
|--------|-------------|
| `-v`, `--debugging` | Display additional debugging information. Debug lines start with `DEBUG:`, and multi-line blocks end with `DEBUG END`. |
| `-q`, `--requirements` | Display requirements for this script. |
| `-h`, `--help` | Display help. |

Unrecognized options print a warning pointing you to `launchanew -h`.

## Examples

```bash
# Basic run, output goes to molecule.out
launchanew molecule.gjf &> molecule.logg &

# Explicit output name, 8 cores, keep checkpoints
launchanew -fp 8 molecule.gjf results/molecule.out &> molecule.logg &

# Re-run reusing old CHK files, no automatic problem solving
launchanew -os molecule.gjf &

# Restore checkpoints from an archive, then run
launchanew -C old_chks.tar molecule.gjf &

# Add Linda workers and split every 5 jobs
launchanew -l "node1,node2" -I 5 molecule.gjf &

# Options in bulk
launchanew -crom molecule.gjf &
```

## Logs

- `$HOME/CalcLog.logg.$HOSTNAME` (previous runs rotate to `.1` and `.2`)
- `$HOME/NowLog.$HOSTNAME` (per-input job counts)
- `$HOME/MemLog.<hostname>.logg` and `$HOME/DiskLog.<hostname>` (with `-m`)

## Exit codes

| Code | Meaning |
|------|---------|
| 0 | Normal exit (also used for help output) |
| 1 | Library not found or not loadable |
| 2 | Output file already exists |
| 3 | Input file missing |
| 4 | `/Gen` basis name missing from the input file (should appear as a comment for output post-processing) |
| 5 | Gaussian executable not in `PATH`, or Gaussian environment variables not set |
| 6 | `GAUSS_SCRDIR` not set |

## Notes

- `launchanew` exits early if another Gaussian is already running (this only works if all Gaussians are the same major release). This is because the practice shows multiple Gaussian instances running on the same node cause mayhem.
- A version history is kept in the comment header of the script.
