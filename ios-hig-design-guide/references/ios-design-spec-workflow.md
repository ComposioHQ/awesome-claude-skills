# iOS Design Spec Workflow (HIG-first)

Use this workflow to turn feature requirements into an iOS-ready design specification.
Open raw content from `apple-hig-ios-fulltext.md` only for sections needed by the feature.

## 1) Define context first

- Product context: app type, audience, feature goal, success metric.
- Platform target: iOS only, or shared with iPadOS/macOS.
- Input constraints: touch only, touch + keyboard, accessories, VoiceOver.

Read first:
- `/design/human-interface-guidelines/designing-for-ios`
- `/design/human-interface-guidelines/getting-started`

## 2) Pull foundational constraints

Always include these constraints in the final spec:

- Accessibility: `/design/human-interface-guidelines/accessibility`
- Layout: `/design/human-interface-guidelines/layout`
- Typography: `/design/human-interface-guidelines/typography`
- Color and contrast: `/design/human-interface-guidelines/color`
- Writing and labels: `/design/human-interface-guidelines/writing`
- Right-to-left support when needed: `/design/human-interface-guidelines/right-to-left`
- Privacy-sensitive UX: `/design/human-interface-guidelines/privacy`

## 3) Select interaction patterns

Choose by feature intent:

- Onboarding and first run: `/design/human-interface-guidelines/onboarding`
- Search-heavy flow: `/design/human-interface-guidelines/searching`
- Settings and preferences: `/design/human-interface-guidelines/settings`
- Account and identity flows: `/design/human-interface-guidelines/managing-accounts`
- Feedback states: `/design/human-interface-guidelines/feedback`, `/design/human-interface-guidelines/loading`
- Notification behavior: `/design/human-interface-guidelines/managing-notifications`

## 4) Select concrete components

Pick only components used by the feature; avoid broad copy-paste of all component rules.

High-frequency iOS components:

- Buttons: `/design/human-interface-guidelines/buttons`
- Tab bars: `/design/human-interface-guidelines/tab-bars`
- Lists and tables: `/design/human-interface-guidelines/lists-and-tables`
- Text fields: `/design/human-interface-guidelines/text-fields`
- Pickers: `/design/human-interface-guidelines/pickers`
- Alerts and action sheets: `/design/human-interface-guidelines/alerts`, `/design/human-interface-guidelines/action-sheets`
- Sheets and popovers: `/design/human-interface-guidelines/sheets`, `/design/human-interface-guidelines/popovers`
- Navigation/search fields: `/design/human-interface-guidelines/search-fields`

## 5) Add system-experience integrations

Check whether the feature needs Apple ecosystem surfaces:

- Widgets: `/design/human-interface-guidelines/widgets`
- Live Activities: `/design/human-interface-guidelines/live-activities`
- Notifications: `/design/human-interface-guidelines/notifications`
- App icons: `/design/human-interface-guidelines/app-icons`
- Sign in with Apple: `/design/human-interface-guidelines/sign-in-with-apple`
- Apple Pay: `/design/human-interface-guidelines/apple-pay`

## 6) Produce a spec with explicit acceptance criteria

Require these sections in final deliverable:

1. User goal and scenario
2. IA and screen map
3. Interaction states (default/loading/error/empty/offline)
4. Component-level rules
5. Accessibility and localization checklist
6. Telemetry/event points and success metrics

## 7) Quick QA gate before handoff

Reject spec drafts that miss any of these:

- No minimum touch target rule
- No dynamic type behavior
- No destructive-action confirmation pattern
- No empty/error/retry state
- No VoiceOver label/hint guidance
- No privacy disclosure for sensitive permissions
