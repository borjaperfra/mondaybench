"""The relevant facts, as fixed sentences shared verbatim by all three levels.

This is what makes the equivalence audit mechanical rather than a matter of
opinion. Every fact the answer depends on is one of these sentences, character
for character, in `compact.txt`, `medium.txt` and `dense.txt`. The levels differ
only in what surrounds them and how far apart they sit.

Two invariants are checked by `equivalence_audit.py`:

1. Every anchor appears **exactly once** in every level.
2. Every occurrence of a protected term - the seven task names, the three
   people, the shared resource - lies **inside** an anchor. So no filler
   sentence anywhere can state, imply or contradict a fact about the tasks or
   the people. Filler can only ever be about other things.

Without invariant 2, "the same problem, more context" would be an assertion.
With it, it is a property of the files.
"""

from __future__ import annotations

ANCHORS = {
    "C01_start_bound": "Work on the cutover may begin no earlier than 07:00.",
    "C02_dur_export": "The export snapshot takes 60 minutes.",
    "C03_dur_schema": "The schema upgrade takes 90 minutes.",
    "C04_dur_index": "The index rebuild takes 120 minutes.",
    "C05_dur_perms": "The permissions sync takes 45 minutes.",
    "C06_dur_smoke": "The smoke checks take 30 minutes.",
    "C07_dur_replay": "The consumer replay takes 75 minutes.",
    "C08_dur_verify": "The final verification takes 60 minutes.",
    "C09_dep_schema": "The schema upgrade cannot start until the export snapshot "
                      "has finished.",
    "C10_dep_index": "The index rebuild cannot start until the schema upgrade has "
                     "finished.",
    "C11_dep_smoke": "The smoke checks cannot start until both the index rebuild "
                     "and the permissions sync have finished.",
    "C12_dep_replay": "The consumer replay cannot start until the smoke checks "
                      "have finished.",
    "C13_dep_verify": "The final verification cannot start until the consumer "
                      "replay has finished.",
    "C14_owner_schema": "Only Priya may run the schema upgrade.",
    "C15_window_priya": "Priya is available from 09:00 to 12:00.",
    "C16_window_owen": "Owen is available from 11:00 to 21:00.",
    "C17_stale_index_owner": "Nadia will run the index rebuild.",
    "C18_update_index_owner": "Update: the index rebuild is now Owen's, not Nadia's.",
    "C19_stale_window_nadia": "Nadia is available from 07:00 to 12:00.",
    "C20_update_window_nadia": "Update: Nadia is out from 10:00 today.",
    "C21_stale_perms_order": "The permissions sync runs before the schema upgrade.",
    "C22_update_perms_order": "Update: the permissions sync must now run after the "
                              "schema upgrade.",
    "C23_resource": "The index rebuild and the permissions sync each need exclusive "
                    "use of the staging cluster, so they cannot overlap.",
    "C24_mechanics": "One person performs one task at a time, no task may be paused "
                     "once it has started, and a task must fit entirely inside the "
                     "availability window of the person performing it.",
    "C25_deadline": "The whole cutover must be complete by 19:00.",
    "C26_optional": "An optional cache warm of 50 minutes can be run on the staging "
                    "cluster, but it is not required for the cutover.",
    "C27_uncertainty": "Nobody has confirmed whether the consumer replay can run at "
                       "double speed, so use the stated duration.",
    "C28_stale_alarm": "The schema upgrade failed during last week's rehearsal.",
    "C29_alarm_explained": "Update: the rehearsal failure was traced to an expired "
                           "credential, which has since been replaced.",
    "C30_open_assignment": "Any of Nadia, Priya and Owen may run any task that is "
                           "not restricted to a named person.",
    "Q_question": "Question: with every task scheduled as early as the rules allow, "
                  "at what clock time does the final verification finish?",
    "Q_format": "End your reply with a single final line in exactly this form:\n"
                "ANSWER: HH:MM",
}

#: Terms that may appear ONLY inside an anchor, in every level.
PROTECTED_TERMS = [
    "export snapshot",
    "schema upgrade",
    "index rebuild",
    "permissions sync",
    "smoke checks",
    "consumer replay",
    "final verification",
    "staging cluster",
    "cache warm",
    "cutover",
    "Nadia",
    "Priya",
    "Owen",
]

#: Which constraint family each anchor belongs to, for the audit's readability.
FAMILIES = {
    "C01_start_bound": "deadline / availability window",
    "C02_dur_export": "duration",
    "C03_dur_schema": "duration",
    "C04_dur_index": "duration",
    "C05_dur_perms": "duration",
    "C06_dur_smoke": "duration",
    "C07_dur_replay": "duration",
    "C08_dur_verify": "duration",
    "C09_dep_schema": "dependency ordering",
    "C10_dep_index": "dependency ordering",
    "C11_dep_smoke": "dependency ordering",
    "C12_dep_replay": "dependency ordering",
    "C13_dep_verify": "dependency ordering",
    "C14_owner_schema": "ownership",
    "C15_window_priya": "availability window",
    "C16_window_owen": "availability window",
    "C17_stale_index_owner": "stale information (superseded)",
    "C18_update_index_owner": "supersession / ownership",
    "C19_stale_window_nadia": "stale information (superseded)",
    "C20_update_window_nadia": "supersession / availability window",
    "C21_stale_perms_order": "stale information (superseded)",
    "C22_update_perms_order": "supersession / dependency ordering",
    "C23_resource": "resource contention",
    "C24_mechanics": "temporal consistency",
    "C25_deadline": "deadline",
    "C26_optional": "plausible but not required (a locally attractive action that "
                    "consumes the contended resource)",
    "C27_uncertainty": "uncertainty that must stay uncertainty",
    "C28_stale_alarm": "plausible but irrelevant alarm",
    "C29_alarm_explained": "supersession that resolves the alarm",
    "C30_open_assignment": "ownership (closes the assignment space)",
    "Q_question": "the question",
    "Q_format": "the output contract",
}

#: Anchors the answer actually depends on, per the solver's drop-one diagnostics.
BINDING = {
    "C14_owner_schema", "C15_window_priya", "C16_window_owen",
    "C18_update_index_owner", "C22_update_perms_order", "C23_resource",
    "C01_start_bound", "C24_mechanics", "C30_open_assignment",
    "C02_dur_export", "C03_dur_schema", "C04_dur_index", "C05_dur_perms",
    "C06_dur_smoke", "C07_dur_replay", "C08_dur_verify",
    "C09_dep_schema", "C10_dep_index", "C11_dep_smoke", "C12_dep_replay",
    "C13_dep_verify",
}
