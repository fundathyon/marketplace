# Catálogo de errores (generado)

<!-- Generado por `make error-catalog` (`go run ./cmd/errcatalog`) desde el código. No editar a mano: lo comprueba `internal/common/errcatalog`. -->

Lista completa de los `error.scope` que el código puede devolver, agrupados por dominio. Mapea por `error.scope` (el contrato estable), no por `message`.

- **HTTP**: los status con los que sale el scope cuando se pueden leer del código (`—` si se decide en tiempo de ejecución).
- **Message**: `descriptivo` sale tal cual (validación, conflicto, formato); `genérico` es un texto fijo (`Internal server error`, `Service temporarily unavailable. Try again later.` o el del status) y el detalle queda en los logs del servidor, ligado al `trace_id` de la respuesta.
- Un `*` marca la parte del scope que se compone en tiempo de ejecución (p. ej. `dto.validate.*` lleva el nombre del DTO).

Formato de la respuesta: [response-format.md](response-format.md). Acciones sugeridas por flujo: [error-scopes.md](error-scopes.md).

**941 scopes** en 57 grupos.

## api_keys

| Scope | HTTP | Message |
|-------|------|---------|
| `api_keys.deactivate.app_id_required` | 400 | descriptivo |
| `api_keys.deactivate.error` | 500 | genérico |
| `api_keys.deactivate.forbidden` | 403 | descriptivo |
| `api_keys.deactivate.id_required` | 400 | descriptivo |
| `api_keys.deactivate.transaction_failed` | 500 | genérico |
| `api_keys.delete.app_id_required` | 400 | descriptivo |
| `api_keys.delete.error` | 500 | genérico |
| `api_keys.delete.forbidden` | 403 | descriptivo |
| `api_keys.delete.id_required` | 400 | descriptivo |
| `api_keys.delete.transaction_failed` | 500 | genérico |
| `api_keys.generate.app_id_required` | 401 | descriptivo |
| `api_keys.generate.transaction_failed` | 500 | genérico |
| `api_keys.get.app_id_required` | 400 | descriptivo |
| `api_keys.get.error` | 500 | genérico |
| `api_keys.get.not_found` | 404 | descriptivo |
| `api_keys.invalid_scopes` | 400 | descriptivo |
| `api_keys.last_full_access_key` | 409 | descriptivo |
| `api_keys.list.app_id_required` | 400 | descriptivo |
| `api_keys.list.error` | 500 | genérico |
| `api_keys.list.invalid_pagination` | 400 | descriptivo |
| `api_keys.rate_limited` | 429 | descriptivo |
| `api_keys.rotate.app_id_required` | 400 | descriptivo |
| `api_keys.rotate.error` | 500 | genérico |
| `api_keys.rotate.generate_error` | 500 | genérico |
| `api_keys.rotate.hash_error` | 500 | genérico |
| `api_keys.rotate.id_required` | 400 | descriptivo |
| `api_keys.rotate.inactive` | 409 | descriptivo |
| `api_keys.rotate.not_found` | 404 | descriptivo |
| `api_keys.rotate.save_error` | 500 | genérico |
| `api_keys.rotate.transaction_failed` | 500 | genérico |
| `api_keys.scope_denied` | 403 | descriptivo |
| `api_keys.scope_escalation` | 403 | descriptivo |
| `api_keys.system_kind.forbidden` | 403 | descriptivo |
| `api_keys.system_kind.invalid` | 422 | descriptivo |
| `api_keys.update.app_id_required` | 400 | descriptivo |
| `api_keys.update.error` | 500 | genérico |
| `api_keys.update.invalid_description` | 400 | descriptivo |
| `api_keys.update.invalid_name` | 400 | descriptivo |
| `api_keys.update.name_taken` | 409 | descriptivo |
| `api_keys.update.not_found` | 404 | descriptivo |
| `api_keys.update.save_error` | 500 | genérico |
| `api_keys.verifier_busy` | 503 | genérico |

## app_auth_configs

| Scope | HTTP | Message |
|-------|------|---------|
| `app_auth_configs.find_error` | 500 | genérico |
| `app_auth_configs.not_found` | 404 | descriptivo |

## app_behaviors

| Scope | HTTP | Message |
|-------|------|---------|
| `app_behaviors.activate_email_code.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.activate_email_code.code_strategy_fixed_not_allowed_in_environment` | 422 | descriptivo |
| `app_behaviors.activate_email_code.error_finding_behavior` | 500 | genérico |
| `app_behaviors.activate_email_code.error_updating_behavior` | 500 | genérico |
| `app_behaviors.activate_email_code.fixed_code_character_class_mismatch` | 422 | descriptivo |
| `app_behaviors.activate_email_code.fixed_code_length_mismatch` | 422 | descriptivo |
| `app_behaviors.activate_email_code.fixed_code_required` | 422 | descriptivo |
| `app_behaviors.activate_magic_link.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.activate_magic_link.error_finding_behavior` | 500 | genérico |
| `app_behaviors.activate_magic_link.error_updating_behavior` | 500 | genérico |
| `app_behaviors.activate_metadata_schema.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.activate_metadata_schema.error_finding_behavior` | 500 | genérico |
| `app_behaviors.activate_metadata_schema.error_updating_behavior` | 500 | genérico |
| `app_behaviors.activate_sessions.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.activate_sessions.error_finding_behavior` | 500 | genérico |
| `app_behaviors.activate_sessions.error_updating_behavior` | 500 | genérico |
| `app_behaviors.activate_sessions.error_updating_tokens_behavior` | 500 | genérico |
| `app_behaviors.activate_sessions.idle_timeout_too_short` | 422 | descriptivo |
| `app_behaviors.activate_testers.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.activate_testers.error_finding_behavior` | 500 | genérico |
| `app_behaviors.activate_testers.error_updating_behavior` | 500 | genérico |
| `app_behaviors.activate_verification.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.activate_verification.code_strategy_fixed_not_allowed_in_environment` | 422 | descriptivo |
| `app_behaviors.activate_verification.error_finding_behavior` | 500 | genérico |
| `app_behaviors.activate_verification.error_updating_behavior` | 500 | genérico |
| `app_behaviors.activate_verification.fixed_code_character_class_mismatch` | 422 | descriptivo |
| `app_behaviors.activate_verification.fixed_code_length_mismatch` | 422 | descriptivo |
| `app_behaviors.activate_verification.fixed_code_required` | 422 | descriptivo |
| `app_behaviors.create.error_creating_app_behavior` | — | descriptivo |
| `app_behaviors.create.use_embedded_auth_endpoint` | 422 | descriptivo |
| `app_behaviors.create.use_geo_access_endpoint` | 422 | descriptivo |
| `app_behaviors.create.use_identity_linking_endpoint` | 422 | descriptivo |
| `app_behaviors.create.use_mfa_endpoint` | 422 | descriptivo |
| `app_behaviors.create.use_security_limits_endpoint` | 422 | descriptivo |
| `app_behaviors.create.use_session_security_endpoint` | 422 | descriptivo |
| `app_behaviors.deactivate_verification.behavior_not_found` | 404 | descriptivo |
| `app_behaviors.deactivate_verification.error_finding_behavior` | 500 | genérico |
| `app_behaviors.deactivate_verification.error_updating_behavior` | 500 | genérico |
| `app_behaviors.email_locale.read_error` | 500 | genérico |
| `app_behaviors.email_locale.save_error` | 500 | genérico |
| `app_behaviors.embedded_auth.invalid_config` | 422 | descriptivo |
| `app_behaviors.embedded_auth.read_error` | 500 | genérico |
| `app_behaviors.embedded_auth.save_error` | 500 | genérico |
| `app_behaviors.example_not_found` | 404 | descriptivo |
| `app_behaviors.geo_access.invalid_config` | 422 | descriptivo |
| `app_behaviors.geo_access.read_error` | 500 | genérico |
| `app_behaviors.geo_access.save_error` | 500 | genérico |
| `app_behaviors.identity_linking.read_error` | 500 | genérico |
| `app_behaviors.identity_linking.save_error` | 500 | genérico |
| `app_behaviors.list.invalid_pagination` | 400 | descriptivo |
| `app_behaviors.mfa.read_error` | 500 | genérico |
| `app_behaviors.mfa.save_error` | 500 | genérico |
| `app_behaviors.security_limits.read_error` | 500 | genérico |
| `app_behaviors.security_limits.save_error` | 500 | genérico |
| `app_behaviors.session_security.read_error` | 500 | genérico |
| `app_behaviors.session_security.save_error` | 500 | genérico |
| `app_behaviors.simple_create.unknown_behavior_code` | 400 | descriptivo |
| `app_behaviors.tokens.invalid_config` | 422 | descriptivo |
| `app_behaviors.tokens.read_error` | 500 | genérico |
| `app_behaviors.tokens.save_error` | 500 | genérico |
| `app_behaviors.update.app_id_required` | — | descriptivo |
| `app_behaviors.update.config_required` | 400 | descriptivo |
| `app_behaviors.update.error_updating` | 500 | genérico |
| `app_behaviors.update.forbidden` | 403 | descriptivo |
| `app_behaviors.update.id_required` | 400 | descriptivo |
| `app_behaviors.update.identifier_mismatch` | 400 | descriptivo |
| `app_behaviors.update.not_found` | 404 | descriptivo |
| `app_behaviors.update.use_embedded_auth_endpoint` | 422 | descriptivo |
| `app_behaviors.update.use_geo_access_endpoint` | 422 | descriptivo |
| `app_behaviors.update.use_identity_linking_endpoint` | 422 | descriptivo |
| `app_behaviors.update.use_mfa_endpoint` | 422 | descriptivo |
| `app_behaviors.update.use_security_limits_endpoint` | 422 | descriptivo |
| `app_behaviors.update.use_session_security_endpoint` | 422 | descriptivo |
| `app_behaviors.update.use_tokens_endpoint` | 422 | descriptivo |

## apps

| Scope | HTTP | Message |
|-------|------|---------|
| `apps.create.conflict` | — | descriptivo |
| `apps.create.internal_error` | 500 | genérico |
| `apps.create.invalid_data` | 400 | descriptivo |
| `apps.create.limit_reached` | 403 | descriptivo |
| `apps.create.transaction_failed` | 500 | genérico |
| `apps.delete.error` | 500 | genérico |
| `apps.delete.missing_id` | 400 | descriptivo |
| `apps.delete.not_found` | 404 | descriptivo |
| `apps.delete.transaction_failed` | 500 | genérico |
| `apps.list.internal_error` | 500 | genérico |
| `apps.list.invalid_pagination` | 400 | descriptivo |
| `apps.list.unauthorized` | 401 | descriptivo |
| `apps.not_found` | 404 | descriptivo |
| `apps.status.invalid` | 400 | descriptivo |
| `apps.status.update_error` | 500 | genérico |
| `apps.suspended` | 403 | descriptivo |
| `apps.tenant.update_error` | 500 | genérico |
| `apps.tenant_ref.invalid` | 400 | descriptivo |
| `apps.update.transaction_failed` | 500 | genérico |

## audit

| Scope | HTTP | Message |
|-------|------|---------|
| `audit.query.app_required` | 400 | descriptivo |
| `audit.query.failed` | 500 | genérico |
| `audit.query.invalid_cursor` | 400 | descriptivo |
| `audit.query.invalid_filter` | 400 | descriptivo |
| `audit.query.local_store_disabled` | 404 | descriptivo |

## auth

| Scope | HTTP | Message |
|-------|------|---------|
| `auth.apikey.invalid` | 401 | descriptivo |
| `auth.rate_limited` | 429 | descriptivo |
| `auth.social.app_id_missing` | 400 | descriptivo |
| `auth.social.audiences_error` | 500 | genérico |
| `auth.social.email_unverified` | 401 | descriptivo |
| `auth.social.id_token_missing` | 400 | descriptivo |
| `auth.social.invalid_audience` | 401 | descriptivo |
| `auth.social.invalid_body` | 400 | descriptivo |
| `auth.social.nonce.consume` | 500 | genérico |
| `auth.social.nonce.create` | 500 | genérico |
| `auth.social.nonce.delete_expired` | 500 | genérico |
| `auth.social.nonce.invalid` | 500 | genérico |
| `auth.social.nonce_error` | 500 | genérico |
| `auth.social.nonce_invalid` | 401 | descriptivo |
| `auth.social.nonce_mismatch` | 401 | descriptivo |
| `auth.social.nonce_required` | 401 | descriptivo |
| `auth.social.oauth_config_disabled` | 400 | descriptivo |
| `auth.social.oauth_config_not_found` | 404 | descriptivo |
| `auth.social.tokens_error` | 500 | genérico |
| `auth.social.unsupported_platform` | 400 | descriptivo |
| `auth.social.unsupported_provider` | 400 | descriptivo |
| `auth.social.validation` | 400 | descriptivo |

## authorize

| Scope | HTTP | Message |
|-------|------|---------|
| `authorize.invalid_token` | 401 | descriptivo |
| `authorize.lookup_error` | 503 | genérico |
| `authorize.user_not_found` | 404 | descriptivo |
| `authorize.validation` | 400 | descriptivo |

## codes

| Scope | HTTP | Message |
|-------|------|---------|
| `codes.consume.error` | 500 | genérico |
| `codes.count_attempt.error` | 500 | genérico |
| `codes.create_code.error_deleting_code` | 500 | genérico |
| `codes.create_code.error_generating_code` | 500 | genérico |
| `codes.create_code.error_saving_code` | 500 | genérico |
| `codes.save.plaintext` | 500 | genérico |

## dashboard

| Scope | HTTP | Message |
|-------|------|---------|
| `dashboard.auth_required` | 401 | descriptivo |
| `dashboard.get_stats.error` | 500 | genérico |

## dto

| Scope | HTTP | Message |
|-------|------|---------|
| `dto.validate.*` | 422 | descriptivo |

## email_access

| Scope | HTTP | Message |
|-------|------|---------|
| `email_access.admin.app_not_found` | 404 | descriptivo |
| `email_access.admin.duplicate_entry` | 409 | descriptivo |
| `email_access.admin.entry_not_found` | 404 | descriptivo |
| `email_access.admin.internal_error` | 500 | genérico |
| `email_access.admin.invalid_access_segment` | 400 | descriptivo |
| `email_access.admin.invalid_app_id` | 400 | descriptivo |
| `email_access.admin.invalid_body` | 400 | descriptivo |
| `email_access.admin.invalid_entry_id` | 400 | descriptivo |
| `email_access.admin.invalid_entry_type` | 400 | descriptivo |
| `email_access.admin.invalid_flow` | 400 | descriptivo |
| `email_access.admin.invalid_list_kind` | 400 | descriptivo |
| `email_access.admin.invalid_mode` | 400 | descriptivo |
| `email_access.admin.invalid_pagination` | 400 | descriptivo |
| `email_access.admin.invalid_target_email` | 400 | descriptivo |
| `email_access.admin.invalid_value` | 400 | descriptivo |
| `email_access.admin.public_domain` | 400 | descriptivo |
| `email_access.app_id_required` | 400 | descriptivo |
| `email_access.denied_by_allowlist` | 403 | descriptivo |
| `email_access.denied_by_blocklist` | 403 | descriptivo |
| `email_access.evaluation_error` | 500 | genérico |
| `email_access.invalid_email` | 400 | descriptivo |

## email_code

| Scope | HTTP | Message |
|-------|------|---------|
| `email_code.already_used` | 401 | descriptivo |
| `email_code.attempts_error` | 500 | genérico |
| `email_code.attempts_exceeded` | 401 | descriptivo |
| `email_code.binding_mismatch` | 401 | descriptivo |
| `email_code.code_gen_error` | 500 | genérico |
| `email_code.cooldown` | 429 | descriptivo |
| `email_code.db_error` | 500 | genérico |
| `email_code.disabled` | 422 | descriptivo |
| `email_code.expired` | 401 | descriptivo |
| `email_code.invalid` | 401 | descriptivo |
| `email_code.invalid_email` | 400 | descriptivo |
| `email_code.invalid_id` | 400 | descriptivo |
| `email_code.invalid_request` | 400 | descriptivo |
| `email_code.invalidate_error` | 500 | genérico |
| `email_code.link_error` | 500 | genérico |
| `email_code.login_method_error` | 500 | genérico |
| `email_code.lookup_error` | 500 | genérico |
| `email_code.mark_used_error` | 500 | genérico |
| `email_code.not_found` | 401 | descriptivo |
| `email_code.rate_limit_error` | 500 | genérico |
| `email_code.rate_limit_exceeded` | 429 | descriptivo |
| `email_code.refresh_save_error` | 500 | genérico |
| `email_code.save_error` | 500 | genérico |
| `email_code.signup_error` | 500 | genérico |
| `email_code.superseded` | 401 | descriptivo |
| `email_code.update_login_method_error` | 500 | genérico |

## email_configs

| Scope | HTTP | Message |
|-------|------|---------|
| `email_configs.delete_error` | 500 | genérico |
| `email_configs.not_found` | 404 | descriptivo |
| `email_configs.removed` | 410 | descriptivo |

## email_locale

| Scope | HTTP | Message |
|-------|------|---------|
| `email_locale.invalid_locale` | 400 | descriptivo |

## email_templates

| Scope | HTTP | Message |
|-------|------|---------|
| `email_templates.delete_error` | 500 | genérico |
| `email_templates.forbidden_variables` | 422 | descriptivo |
| `email_templates.html_required` | 422 | descriptivo |
| `email_templates.html_too_large` | 422 | descriptivo |
| `email_templates.invalid_locale` | 422 | descriptivo |
| `email_templates.missing_required_variables` | 422 | descriptivo |
| `email_templates.not_found` | 404 | descriptivo |
| `email_templates.preview.unknown_template` | 404 | descriptivo |
| `email_templates.pro_required` | 403 | descriptivo |
| `email_templates.sanitization_failed` | 422 | descriptivo |
| `email_templates.save_error` | 500 | genérico |
| `email_templates.subject_invalid` | 422 | descriptivo |
| `email_templates.subject_required` | 422 | descriptivo |
| `email_templates.test.no_email_config` | 409 | descriptivo |
| `email_templates.test.rate_limited` | 429 | descriptivo |
| `email_templates.test.send_failed` | 502 | genérico |
| `email_templates.test_email_required` | 422 | descriptivo |
| `email_templates.themes.invalid_branding` | 422 | descriptivo |
| `email_templates.themes.pro_required` | 403 | descriptivo |
| `email_templates.themes.save_error` | 500 | genérico |
| `email_templates.themes.unknown_theme` | 422 | descriptivo |
| `email_templates.unknown_template` | 404 | descriptivo |

## email_themes

| Scope | HTTP | Message |
|-------|------|---------|
| `email_themes.save_error` | 500 | genérico |

## emails

| Scope | HTTP | Message |
|-------|------|---------|
| `emails.activate.error_code_expired` | 400 | descriptivo |
| `emails.activate.error_code_not_found` | 404 | descriptivo |
| `emails.activate.error_email_not_found` | — | descriptivo |
| `emails.activate.error_getting_codes` | 500 | genérico |
| `emails.activate.error_getting_email` | 500 | genérico |
| `emails.activate.error_getting_login_method` | 500 | genérico |
| `emails.activate.error_invalid_code` | 400 | descriptivo |
| `emails.activate.error_login_not_found` | — | descriptivo |
| `emails.activate.error_saving_code` | 500 | genérico |
| `emails.activate.error_too_many_attempts` | — | descriptivo |
| `emails.activate.transaction_failed` | 500 | genérico |
| `emails.activate_v2.error_code_not_found` | 404 | descriptivo |
| `emails.activate_v2.error_code_not_valid` | 400 | descriptivo |
| `emails.activate_v2.error_generating_token` | 500 | genérico |
| `emails.activate_v2.error_getting_codes` | 500 | genérico |
| `emails.activate_v2.error_getting_email` | 500 | genérico |
| `emails.activate_v2.error_pending_registration_not_found` | 404 | descriptivo |
| `emails.activate_v2.error_too_many_attempts` | — | descriptivo |
| `emails.config_not_found` | 404 | descriptivo |
| `emails.confirm_password.error_code_not_found` | 404 | descriptivo |
| `emails.confirm_password.error_code_not_valid` | 401 | descriptivo |
| `emails.confirm_password.error_email_not_found` | 404 | descriptivo |
| `emails.confirm_password.error_getting_code` | 500 | genérico |
| `emails.confirm_password.error_getting_email` | 500 | genérico |
| `emails.confirm_password.error_getting_login_method` | 500 | genérico |
| `emails.confirm_password.error_getting_user` | 500 | genérico |
| `emails.confirm_password.error_hashing_password` | 500 | genérico |
| `emails.confirm_password.error_invalid_password` | 400 | descriptivo |
| `emails.confirm_password.error_login_method_not_found` | 404 | descriptivo |
| `emails.confirm_password.error_too_many_attempts` | — | descriptivo |
| `emails.confirm_password.error_updating_code` | 500 | genérico |
| `emails.confirm_password.error_updating_login_method` | 500 | genérico |
| `emails.confirm_password.error_updating_password` | 500 | genérico |
| `emails.confirm_password.transaction_failed` | 500 | genérico |
| `emails.create_email.error_matching_email` | 500 | genérico |
| `emails.create_email.error_saving_user` | 500 | genérico |
| `emails.create_login.error_saving_login` | 500 | genérico |
| `emails.create_refresh_token.error_saving_code` | 500 | genérico |
| `emails.create_user.error_matching_role` | 500 | genérico |
| `emails.create_user.error_saving_user` | 500 | genérico |
| `emails.create_user.role_not_found` | 404 | descriptivo |
| `emails.email_not_found` | 404 | descriptivo |
| `emails.email_not_verified` | 401 | descriptivo |
| `emails.error_creating_refresh_token` | 500 | genérico |
| `emails.error_finding_config` | 500 | genérico |
| `emails.error_generating_tokens` | 500 | genérico |
| `emails.error_getting_email` | 500 | genérico |
| `emails.error_getting_login` | 500 | genérico |
| `emails.gmail_config_missing` | 400 | descriptivo |
| `emails.invalid_password` | 401 | descriptivo |
| `emails.login_not_found` | 404 | descriptivo |
| `emails.mailgun_config_missing` | 400 | descriptivo |
| `emails.passwordless.transaction_failed` | 500 | genérico |
| `emails.resend.already_active` | 409 | descriptivo |
| `emails.resend.rate_limited` | 429 | descriptivo |
| `emails.resend.user_not_found` | 404 | descriptivo |
| `emails.resend_activation_code.error_generating_code` | 500 | genérico |
| `emails.resend_activation_code.error_getting_codes` | 500 | genérico |
| `emails.resend_activation_code.error_getting_email` | 500 | genérico |
| `emails.resend_activation_code.error_getting_user` | 500 | genérico |
| `emails.resend_activation_code.error_saving_code` | 500 | genérico |
| `emails.reserved_domain` | 422 | descriptivo |
| `emails.reset_password.error_generating_code` | 500 | genérico |
| `emails.reset_password.error_getting_codes` | 500 | genérico |
| `emails.reset_password.error_getting_email` | 500 | genérico |
| `emails.reset_password.error_getting_user` | 500 | genérico |
| `emails.reset_password.error_saving_code` | 500 | genérico |
| `emails.reset_password.rate_limited` | 429 | descriptivo |
| `emails.reset_password.transaction_failed` | 500 | genérico |
| `emails.set_password.error_creating_refresh_token` | 500 | genérico |
| `emails.set_password.error_generating_tokens` | 500 | genérico |
| `emails.set_password.error_getting_pending_registration` | 500 | genérico |
| `emails.set_password.error_hashing_password` | 500 | genérico |
| `emails.set_password.error_invalid_password` | 400 | descriptivo |
| `emails.set_password.error_invalid_token` | 401 | descriptivo |
| `emails.set_password.error_pending_registration_not_found` | 404 | descriptivo |
| `emails.set_password.error_saving_email` | 500 | genérico |
| `emails.set_password.error_saving_login_method` | 500 | genérico |
| `emails.set_password.transaction_failed` | 500 | genérico |
| `emails.set_password_from_reset.error_app_id_mismatch` | 401 | descriptivo |
| `emails.set_password_from_reset.error_hashing_password` | 500 | genérico |
| `emails.set_password_from_reset.error_invalid_password` | 400 | descriptivo |
| `emails.set_password_from_reset.error_invalid_token` | 401 | descriptivo |
| `emails.set_password_from_reset.error_invalid_token_purpose` | 401 | descriptivo |
| `emails.set_password_from_reset.error_token_already_used` | 401 | descriptivo |
| `emails.set_password_from_reset.error_updating_code` | 500 | genérico |
| `emails.set_password_from_reset.error_updating_login_method` | 500 | genérico |
| `emails.set_password_from_reset.error_updating_password` | 500 | genérico |
| `emails.signin.error_checking_password` | 500 | genérico |
| `emails.signin.error_creating_refresh_token` | — | descriptivo |
| `emails.signin.error_email_not_verified` | — | descriptivo |
| `emails.signin.error_generating_tokens` | — | descriptivo |
| `emails.signin.error_getting_email` | — | descriptivo |
| `emails.signin.error_getting_login` | — | descriptivo |
| `emails.signin.error_getting_user` | 500 | genérico |
| `emails.signin.error_login_not_found` | — | descriptivo |
| `emails.signin.invalid_credentials` | 401 | descriptivo |
| `emails.signup.app_not_found` | 404 | descriptivo |
| `emails.signup.email_already_exists` | 409 | descriptivo |
| `emails.signup.error_creating_email_for_oauth_user` | 500 | genérico |
| `emails.signup.error_creating_login_refresh_token_and_code` | 500 | genérico |
| `emails.signup.error_creating_user_and_email` | 500 | genérico |
| `emails.signup.error_extracting_verification_config` | 500 | genérico |
| `emails.signup.error_generating_email` | 500 | genérico |
| `emails.signup.error_generating_user` | 500 | genérico |
| `emails.signup.error_getting_email_config` | 500 | genérico |
| `emails.signup.error_hashing_password` | 500 | genérico |
| `emails.signup.error_invalid_password` | 400 | descriptivo |
| `emails.signup.error_oauth_user_not_found` | 500 | genérico |
| `emails.signup.error_validating_email_available` | 422 | genérico (interno) |
| `emails.signup.internal_error` | 500 | genérico |
| `emails.signup.transaction_failed` | 500 | genérico |
| `emails.signup_without_verification.error_creating_login_and_refresh` | 500 | genérico |
| `emails.signup_without_verification.error_creating_user_and_email` | 500 | genérico |
| `emails.signup_without_verification.error_generating_email` | 500 | genérico |
| `emails.signup_without_verification.error_generating_tokens` | 500 | genérico |
| `emails.signup_without_verification.error_generating_user` | 500 | genérico |
| `emails.signup_without_verification.error_marking_login_verified` | 500 | genérico |
| `emails.validate_reset_code.error_generating_token` | 500 | genérico |
| `emails.validate_reset_code.error_getting_user` | 500 | genérico |
| `emails.validation.metadata_schema` | 422 | descriptivo |
| `emails.validation.weak_password` | 422 | descriptivo |

## embedded_auth

| Scope | HTTP | Message |
|-------|------|---------|
| `embedded_auth.disabled` | 403 | descriptivo |
| `embedded_auth.lookup_error` | 503 | genérico |
| `embedded_auth.magic_link.challenge_required` | 422 | descriptivo |
| `embedded_auth.oauth.nonce_required` | 400 | descriptivo |
| `embedded_auth.oauth.provider_not_allowed` | 403 | descriptivo |
| `embedded_auth.origin.not_allowed` | 403 | descriptivo |
| `embedded_auth.publishable_key.required` | 401 | descriptivo |
| `embedded_auth.redirect.check_error` | 500 | genérico |
| `embedded_auth.redirect.not_allowed` | 403 | descriptivo |
| `embedded_auth.unavailable` | 503 | genérico |

## entitlements

| Scope | HTTP | Message |
|-------|------|---------|
| `entitlements.disabled` | 409 | descriptivo |
| `entitlements.lookup_error` | 500 | genérico |
| `entitlements.not_found` | 404 | descriptivo |
| `entitlements.period.invalid` | 400 | descriptivo |
| `entitlements.provider_unavailable` | 502 | genérico |
| `entitlements.tenant_ref.invalid` | 400 | descriptivo |

## exits_user

| Scope | HTTP | Message |
|-------|------|---------|
| `exits_user.criteria_error` | 500 | genérico |
| `exits_user.not_found` | 404 | descriptivo |
| `exits_user.not_verified` | 404 | descriptivo |

## geo_access

| Scope | HTTP | Message |
|-------|------|---------|
| `geo_access.country_not_allowed` | 403 | descriptivo |
| `geo_access.lookup_error` | 503 | genérico |
| `geo_access.unknown_country` | 403 | descriptivo |

## http

| Scope | HTTP | Message |
|-------|------|---------|
| `http.request.body_too_large` | 413 | descriptivo |

## identity_link

| Scope | HTTP | Message |
|-------|------|---------|
| `identity_link.create_new` | 500 | genérico |
| `identity_link.link_existing` | 500 | genérico |

## identity_linking

| Scope | HTTP | Message |
|-------|------|---------|
| `identity_linking.invalid_mode` | 400 | descriptivo |
| `identity_linking.lookup_error` | 503 | genérico |

## login_events

| Scope | HTTP | Message |
|-------|------|---------|
| `login_events.list.error` | 500 | genérico |
| `login_events.summary.error` | 500 | genérico |
| `login_events.unavailable` | 500 | genérico |

## magic_link

| Scope | HTTP | Message |
|-------|------|---------|
| `magic_link.already_used` | 401 | descriptivo |
| `magic_link.binding_mismatch` | 401 | descriptivo |
| `magic_link.db_error` | 500 | genérico |
| `magic_link.disabled` | 422 | descriptivo |
| `magic_link.expired` | 401 | descriptivo |
| `magic_link.invalid_email` | 400 | descriptivo |
| `magic_link.invalid_id` | 400 | descriptivo |
| `magic_link.invalid_redirect_path` | 400 | descriptivo |
| `magic_link.invalid_token` | 400 | descriptivo |
| `magic_link.link_error` | 500 | genérico |
| `magic_link.login_method_error` | 500 | genérico |
| `magic_link.lookup_error` | 500 | genérico |
| `magic_link.mark_used_error` | 500 | genérico |
| `magic_link.not_found` | 401 | descriptivo |
| `magic_link.rate_limit_error` | 500 | genérico |
| `magic_link.rate_limit_exceeded` | 429 | descriptivo |
| `magic_link.refresh_save_error` | 500 | genérico |
| `magic_link.save_error` | 500 | genérico |
| `magic_link.signup_error` | 500 | genérico |
| `magic_link.token_gen_error` | 500 | genérico |
| `magic_link.update_login_method_error` | 500 | genérico |

## mcp_authorization

| Scope | HTTP | Message |
|-------|------|---------|
| `mcp_authorization.approve` | 500 | genérico |
| `mcp_authorization.approve.code` | 500 | genérico |
| `mcp_authorization.approve.not_pending` | 409 | descriptivo |
| `mcp_authorization.approve.scope_not_allowed_for_user` | 422 | descriptivo |
| `mcp_authorization.approve.scope_not_requested` | 422 | descriptivo |
| `mcp_authorization.approve.scope_required` | 422 | descriptivo |
| `mcp_authorization.approve.user_token_invalid` | — | descriptivo |
| `mcp_authorization.burn` | 500 | genérico |
| `mcp_authorization.consume` | 500 | genérico |
| `mcp_authorization.create` | 500 | genérico |
| `mcp_authorization.delete_expired` | 500 | genérico |
| `mcp_authorization.deny` | 500 | genérico |
| `mcp_authorization.deny.not_pending` | 409 | descriptivo |
| `mcp_authorization.expired` | 410 | descriptivo |
| `mcp_authorization.find` | 500 | genérico |
| `mcp_authorization.find_code` | 500 | genérico |
| `mcp_authorization.invalid` | 400 | genérico (interno) |
| `mcp_authorization.not_found` | 404 | descriptivo |
| `mcp_authorization.user_lookup` | 500 | genérico |
| `mcp_authorization.user_not_found` | 401 | descriptivo |
| `mcp_authorization.user_token_invalid` | 401 | descriptivo |
| `mcp_authorization.user_token_required` | 401 | descriptivo |

## mcp_connections

| Scope | HTTP | Message |
|-------|------|---------|
| `mcp_connections.count` | 500 | genérico |
| `mcp_connections.count_by_user` | 500 | genérico |
| `mcp_connections.create` | 500 | genérico |
| `mcp_connections.find` | 500 | genérico |
| `mcp_connections.invalid` | 400 | genérico (interno) |
| `mcp_connections.list` | 500 | genérico |
| `mcp_connections.me.invalid_token` | 401 | descriptivo |
| `mcp_connections.me.missing_token` | 401 | descriptivo |
| `mcp_connections.me.user_id_missing` | 401 | descriptivo |
| `mcp_connections.not_found` | 404 | descriptivo |
| `mcp_connections.regrant` | 500 | genérico |
| `mcp_connections.revoke` | 500 | genérico |
| `mcp_connections.summary` | 500 | genérico |
| `mcp_connections.summary.too_many` | 400 | descriptivo |
| `mcp_connections.summary.user_ids_required` | 400 | descriptivo |
| `mcp_connections.touch` | 500 | genérico |

## mcp_resources

| Scope | HTTP | Message |
|-------|------|---------|
| `mcp_resources.create` | 500 | genérico |
| `mcp_resources.delete` | 500 | genérico |
| `mcp_resources.duplicate_resource_url` | 409 | descriptivo |
| `mcp_resources.duplicate_scope_key` | — | descriptivo |
| `mcp_resources.find` | 500 | genérico |
| `mcp_resources.invalid` | 400 | descriptivo |
| `mcp_resources.invalid_access_ttl` | 422 | descriptivo |
| `mcp_resources.invalid_client_domain` | 422 | descriptivo |
| `mcp_resources.invalid_login_url` | 422 | descriptivo |
| `mcp_resources.invalid_redirect_domain` | 422 | descriptivo |
| `mcp_resources.invalid_resource_url` | 422 | descriptivo |
| `mcp_resources.invalid_scope` | 400 | descriptivo |
| `mcp_resources.invalid_scope_key` | — | descriptivo |
| `mcp_resources.invalid_scope_label` | — | descriptivo |
| `mcp_resources.list` | 500 | genérico |
| `mcp_resources.not_found` | 404 | descriptivo |
| `mcp_resources.replace_scopes` | 500 | genérico |
| `mcp_resources.roles_lookup` | 500 | genérico |
| `mcp_resources.set_verification` | 500 | genérico |
| `mcp_resources.unknown_role` | — | descriptivo |
| `mcp_resources.update` | 500 | genérico |
| `mcp_resources.verify.blocked_destination` | 422 | descriptivo |
| `mcp_resources.verify_report` | 400 | descriptivo |

## metrics

| Scope | HTTP | Message |
|-------|------|---------|
| `metrics.auth_required` | 401 | descriptivo |
| `metrics.query.failed` | 500 | genérico |
| `metrics.query.invalid` | 400 | descriptivo |
| `metrics.query.invalid_tz` | 400 | descriptivo |
| `metrics.query.range_too_large` | 400 | descriptivo |
| `metrics.unknown_metric` | 404 | descriptivo |
| `metrics.webhook_not_found` | 404 | descriptivo |

## mfa

| Scope | HTTP | Message |
|-------|------|---------|
| `mfa.already_enrolled` | 409 | descriptivo |
| `mfa.enrollment_not_started` | 409 | descriptivo |
| `mfa.enrollment_required` | 409 | descriptivo |
| `mfa.internal_error` | 500 | genérico |
| `mfa.invalid_code` | 401 | descriptivo |
| `mfa.invalid_flow` | 400 | descriptivo |
| `mfa.invalid_method` | 400 | descriptivo |
| `mfa.invalid_mode` | 400 | descriptivo |
| `mfa.invalid_token` | 401 | descriptivo |
| `mfa.lookup_error` | 503 | genérico |
| `mfa.too_many_attempts` | 429 | descriptivo |

## oauth

| Scope | HTTP | Message |
|-------|------|---------|
| `oauth.exchange.app_required` | 401 | descriptivo |
| `oauth.exchange.code_expired` | 400 | descriptivo |
| `oauth.exchange.code_used` | 400 | descriptivo |
| `oauth.exchange.error` | 500 | genérico |
| `oauth.exchange.invalid_code` | 400 | descriptivo |
| `oauth.exchange.redirect_mismatch` | 400 | descriptivo |
| `oauth.exchange.validation` | 400 | descriptivo |

## oauth_clients

| Scope | HTTP | Message |
|-------|------|---------|
| `oauth_clients.count` | 500 | genérico |
| `oauth_clients.delete_unused` | 500 | genérico |
| `oauth_clients.disable` | 500 | genérico |
| `oauth_clients.find` | 500 | genérico |
| `oauth_clients.generate` | 500 | genérico |
| `oauth_clients.invalid` | 400 | genérico (interno) |
| `oauth_clients.invalid_name` | 422 | descriptivo |
| `oauth_clients.invalid_redirect_uris` | 422 | descriptivo |
| `oauth_clients.list` | 500 | genérico |
| `oauth_clients.not_found` | 404 | descriptivo |
| `oauth_clients.redirect_domain_not_allowed` | 422 | descriptivo |
| `oauth_clients.save` | 500 | genérico |
| `oauth_clients.touch` | 500 | genérico |

## oauth_configs

| Scope | HTTP | Message |
|-------|------|---------|
| `oauth_configs.create.app_id_required` | 400 | descriptivo |
| `oauth_configs.delete.app_id_required` | 400 | descriptivo |
| `oauth_configs.delete.error` | 500 | genérico |
| `oauth_configs.delete.error_redirect_urls` | 500 | genérico |
| `oauth_configs.delete.id_required` | 400 | descriptivo |
| `oauth_configs.disable.app_id_required` | 400 | descriptivo |
| `oauth_configs.disable.error` | 500 | genérico |
| `oauth_configs.disable.id_required` | 400 | descriptivo |
| `oauth_configs.get_link.api_key_required` | 401 | descriptivo |
| `oauth_configs.get_link.platform_required` | 400 | descriptivo |
| `oauth_configs.get_link.provider_required` | 400 | descriptivo |
| `oauth_configs.list.app_id_required` | 400 | descriptivo |
| `oauth_configs.migration.app_id_required` | 400 | descriptivo |
| `oauth_configs.migration.clear_error` | 500 | genérico |
| `oauth_configs.migration.insert_error` | 500 | genérico |
| `oauth_configs.migration.list_error` | 500 | genérico |
| `oauth_configs.migration.redirect_list_error` | 500 | genérico |
| `oauth_configs.redirects.app_id_required` | 400 | descriptivo |
| `oauth_configs.redirects.config_not_found` | 404 | descriptivo |
| `oauth_configs.redirects.id_required` | 400 | descriptivo |
| `oauth_configs.redirects.list_error` | 500 | genérico |
| `oauth_configs.update.app_id_required` | 400 | descriptivo |
| `oauth_configs.update.error` | 500 | genérico |
| `oauth_configs.update.error_redirect_urls` | 500 | genérico |
| `oauth_configs.update.fields_required` | 400 | descriptivo |
| `oauth_configs.update.id_required` | 400 | descriptivo |

## oauth_native_audiences

| Scope | HTTP | Message |
|-------|------|---------|
| `oauth_native_audiences.app_id_required` | 400 | descriptivo |
| `oauth_native_audiences.config_not_found` | 404 | descriptivo |
| `oauth_native_audiences.delete_error` | 500 | genérico |
| `oauth_native_audiences.duplicate` | — | descriptivo |
| `oauth_native_audiences.invalid_audience` | 400 | descriptivo |
| `oauth_native_audiences.invalid_body` | 400 | descriptivo |
| `oauth_native_audiences.invalid_id` | 400 | descriptivo |
| `oauth_native_audiences.invalid_platform` | 400 | descriptivo |
| `oauth_native_audiences.list_error` | 500 | genérico |
| `oauth_native_audiences.model_map` | 500 | genérico |
| `oauth_native_audiences.not_found` | 404 | descriptivo |
| `oauth_native_audiences.save_error` | — | descriptivo |
| `oauth_native_audiences.validation` | 400 | descriptivo |

## oauths

| Scope | HTTP | Message |
|-------|------|---------|
| `oauths.callback.config_not_found` | 404 | descriptivo |
| `oauths.callback.create_identity_failed` | 500 | genérico |
| `oauths.callback.exchange_code_error` | 500 | genérico |
| `oauths.callback.exchange_unavailable` | 500 | genérico |
| `oauths.callback.external_id_missing` | 400 | descriptivo |
| `oauths.callback.get_user_info` | 500 | genérico |
| `oauths.callback.identity_linker_missing` | 500 | genérico |
| `oauths.callback.invalid_redirect` | 500 | genérico |
| `oauths.callback.invalid_rt` | 400 | descriptivo |
| `oauths.callback.invalid_state` | 400 | descriptivo |
| `oauths.callback.link_identity_failed` | 500 | genérico |
| `oauths.callback.login_failed` | — | descriptivo |
| `oauths.callback.login_method_lookup_failed` | 500 | genérico |
| `oauths.callback.login_method_not_found` | 500 | genérico |
| `oauths.callback.no_redirect_uri` | 400 | descriptivo |
| `oauths.callback.role_not_found` | 500 | genérico |
| `oauths.callback.state_error` | 500 | genérico |
| `oauths.callback.state_mismatch` | 403 | descriptivo |
| `oauths.callback.tokens_error` | 500 | genérico |
| `oauths.callback.transaction_failed` | 500 | genérico |
| `oauths.callback.unsupported_provider` | 400 | descriptivo |
| `oauths.callback.user_not_found` | 500 | genérico |
| `oauths.callback.validation` | 400 | descriptivo |
| `oauths.config_not_found` | 404 | descriptivo |
| `oauths.create.error_creating_oauth_config` | — | descriptivo |
| `oauths.create.error_redirect_urls` | 500 | genérico |
| `oauths.error_finding_api_key` | 500 | genérico |
| `oauths.error_finding_config` | 500 | genérico |
| `oauths.flow.consume` | 500 | genérico |
| `oauths.flow.create` | 500 | genérico |
| `oauths.flow.delete_expired` | 500 | genérico |
| `oauths.flow.find` | 500 | genérico |
| `oauths.flow.invalid` | 500 | genérico |
| `oauths.flow.not_found` | 400 | descriptivo |
| `oauths.get_link.error_client` | 500 | genérico |
| `oauths.get_link.error_credentials` | 500 | genérico |
| `oauths.get_link.error_link` | 500 | genérico |
| `oauths.get_link.invalid_platform` | 400 | descriptivo |
| `oauths.get_link.invalid_provider` | 400 | descriptivo |
| `oauths.get_link.invalid_redirect_selector` | 400 | descriptivo |
| `oauths.get_link.redirect_not_found` | 400 | descriptivo |
| `oauths.get_link.rt_not_found` | 400 | descriptivo |
| `oauths.google_config_missing` | 400 | descriptivo |
| `oauths.invalid_api_key` | 401 | descriptivo |
| `oauths.invalid_api_key_format` | 401 | descriptivo |
| `oauths.invalid_provider` | 400 | descriptivo |
| `oauths.link.app_id_required` | 400 | descriptivo |
| `oauths.link.platform_required` | 400 | descriptivo |
| `oauths.link.provider_required` | 400 | descriptivo |
| `oauths.list.error` | 500 | genérico |
| `oauths.list.redirects_error` | 500 | genérico |
| `oauths.start.config_not_found` | 404 | descriptivo |
| `oauths.start.error_client` | 500 | genérico |
| `oauths.start.error_generating_state` | 500 | genérico |
| `oauths.start.error_link` | 500 | genérico |
| `oauths.start.error_saving_flow` | 500 | genérico |
| `oauths.start.invalid_platform` | 400 | descriptivo |
| `oauths.start.invalid_rt` | 400 | descriptivo |
| `oauths.start.rt_not_found` | 400 | descriptivo |

## password

| Scope | HTTP | Message |
|-------|------|---------|
| `password.breached` | 400 | descriptivo |

## password_policy

| Scope | HTTP | Message |
|-------|------|---------|
| `password_policy.invalid_configuration` | 500 | genérico |
| `password_policy.matching_failed` | 500 | genérico |
| `password_policy.repository_not_configured` | 500 | genérico |

## pending_registrations

| Scope | HTTP | Message |
|-------|------|---------|
| `pending_registrations.create.error_generating_code` | 500 | genérico |
| `pending_registrations.create.error_getting_roles` | 500 | genérico |
| `pending_registrations.create.error_saving_code` | 500 | genérico |
| `pending_registrations.create.error_saving_pending_registration` | 500 | genérico |
| `pending_registrations.create.error_saving_user` | 500 | genérico |
| `pending_registrations.create.role_not_found` | 404 | descriptivo |

## policies

| Scope | HTTP | Message |
|-------|------|---------|
| `policies.create.error_creating_policy` | — | descriptivo |
| `policies.create.transaction_failed` | 500 | genérico |
| `policies.delete.error_deleting_policy` | 500 | genérico |
| `policies.delete.error_getting_policy` | — | descriptivo |
| `policies.delete.not_found` | — | descriptivo |
| `policies.delete.transaction_failed` | 500 | genérico |
| `policies.update.already_exists` | 409 | descriptivo |
| `policies.update.error_getting_policy` | — | descriptivo |
| `policies.update.error_updating_policy` | — | descriptivo |
| `policies.update.not_found` | — | descriptivo |
| `policies.update.transaction_failed` | 500 | genérico |
| `policies.update.validation` | 400 | descriptivo |

## public_key_jwt

| Scope | HTTP | Message |
|-------|------|---------|
| `public_key_jwt.api_key_required` | 401 | descriptivo |
| `public_key_jwt.invalid_app_id` | 500 | genérico |
| `public_key_jwt.not_found` | 404 | descriptivo |
| `public_key_jwt.unauthorized` | 401 | descriptivo |

## quota

| Scope | HTTP | Message |
|-------|------|---------|
| `quota.api_keys_exceeded` | 403 | descriptivo |
| `quota.feature_not_in_plan` | 403 | descriptivo |
| `quota.oauth_providers_exceeded` | 403 | descriptivo |
| `quota.roles_exceeded` | 403 | descriptivo |
| `quota.tenant_read_only` | 403 | descriptivo |
| `quota.users_exceeded` | 403 | descriptivo |
| `quota.webhooks_exceeded` | 403 | descriptivo |

## redirect_urls

| Scope | HTTP | Message |
|-------|------|---------|
| `redirect_urls.invalid_app_id` | 400 | descriptivo |
| `redirect_urls.invalid_id` | 400 | descriptivo |
| `redirect_urls.model_map` | 500 | genérico |
| `redirect_urls.not_found` | 404 | descriptivo |
| `redirect_urls.sync.generator_required` | 500 | genérico |

## refresh_tokens

| Scope | HTTP | Message |
|-------|------|---------|
| `refresh_tokens.create.failed_to_get_login_method` | 500 | genérico |
| `refresh_tokens.create.failed_to_get_refresh_token` | 500 | genérico |
| `refresh_tokens.create.failed_to_get_user` | 500 | genérico |
| `refresh_tokens.create.failed_to_validate_token` | 401 | descriptivo |
| `refresh_tokens.create.generation_invalid` | 401 | descriptivo |
| `refresh_tokens.create.id_invalid` | 401 | descriptivo |
| `refresh_tokens.create.idle_timeout` | 401 | descriptivo |
| `refresh_tokens.create.login_method_not_found` | 404 | descriptivo |
| `refresh_tokens.create.refresh_token_not_found` | 404 | descriptivo |
| `refresh_tokens.create.reuse_detected` | 401 | descriptivo |
| `refresh_tokens.create.revoked` | 401 | descriptivo |
| `refresh_tokens.create.rotation_error` | 500 | genérico |
| `refresh_tokens.create.sign_error` | 500 | genérico |
| `refresh_tokens.info.email_not_found` | 401 | descriptivo |
| `refresh_tokens.info.entity_id` | 401 | descriptivo |
| `refresh_tokens.info.entity_type` | 401 | descriptivo |
| `refresh_tokens.info.get_email` | 401 | genérico (interno) |
| `refresh_tokens.info.get_login_method` | 401 | genérico (interno) |
| `refresh_tokens.info.get_user` | 401 | genérico (interno) |
| `refresh_tokens.info.id` | 401 | descriptivo |
| `refresh_tokens.info.login_method_not_found` | 401 | descriptivo |
| `refresh_tokens.info.marshal_email` | 401 | genérico (interno) |
| `refresh_tokens.info.token_type` | 401 | descriptivo |
| `refresh_tokens.info.unmarshal_email` | 401 | genérico (interno) |
| `refresh_tokens.info.user_id` | 401 | descriptivo |
| `refresh_tokens.info.user_not_found` | 401 | descriptivo |
| `refresh_tokens.info.validate_token` | 401 | descriptivo |
| `refresh_tokens.logout.error` | 500 | genérico |
| `refresh_tokens.logout.id_invalid` | 401 | descriptivo |
| `refresh_tokens.logout.missing_token` | 401 | descriptivo |
| `refresh_tokens.logout.not_found` | 404 | descriptivo |
| `refresh_tokens.logout.token` | 401 | descriptivo |
| `refresh_tokens.open_oauth_session.save_error` | 500 | genérico |
| `refresh_tokens.revoke.error` | 500 | genérico |
| `refresh_tokens.revoke.forbidden` | 404 | descriptivo |
| `refresh_tokens.revoke.not_found` | 404 | descriptivo |
| `refresh_tokens.revoke_by_id.app_id_required` | 400 | descriptivo |
| `refresh_tokens.revoke_by_id.id_required` | 400 | descriptivo |
| `refresh_tokens.revoke_by_token.app_id_required` | 400 | descriptivo |
| `refresh_tokens.revoke_by_token.id_invalid` | 401 | descriptivo |
| `refresh_tokens.revoke_by_token.id_missing` | 401 | descriptivo |
| `refresh_tokens.revoke_by_token.token` | 401 | descriptivo |
| `refresh_tokens.validate.entity_type` | 401 | genérico (seguridad) |
| `refresh_tokens.validate.lookup_error` | 503 | genérico |
| `refresh_tokens.validate.revoked` | 401 | descriptivo |
| `refresh_tokens.validate.token` | 401 | descriptivo |
| `refresh_tokens.validate.token_type` | 401 | genérico (seguridad) |
| `refresh_tokens.validate_refresh.generation_invalid` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.id_invalid` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.id_missing` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.idle_timeout` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.not_found` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.revoked` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.rotated` | 401 | descriptivo |
| `refresh_tokens.validate_refresh.token` | 401 | descriptivo |

## role_policies

| Scope | HTTP | Message |
|-------|------|---------|
| `role_policies.create.error_creating_policy` | 500 | genérico |
| `role_policies.create.error_getting_policy` | 500 | genérico |
| `role_policies.create.error_getting_role` | 500 | genérico |
| `role_policies.create.policy_not_found` | 404 | descriptivo |
| `role_policies.create.policy_not_found_in_app` | 404 | descriptivo |
| `role_policies.create.role_not_found` | 404 | descriptivo |
| `role_policies.create.role_not_found_in_app` | 404 | descriptivo |
| `role_policies.info.error_getting_policies` | 500 | genérico |
| `role_policies.info.error_getting_policy` | 500 | genérico |
| `role_policies.info.error_getting_role` | 500 | genérico |
| `role_policies.info.role_not_found` | 404 | descriptivo |
| `role_policies.remove.error` | 500 | genérico |
| `role_policies.remove.not_found` | 404 | descriptivo |

## roles

| Scope | HTTP | Message |
|-------|------|---------|
| `roles.create.error_creating_role` | — | descriptivo |
| `roles.create.transaction_failed` | 500 | genérico |
| `roles.delete.default_role_forbidden` | 403 | descriptivo |
| `roles.delete.error` | 500 | genérico |
| `roles.delete.id_required` | 400 | descriptivo |
| `roles.delete.not_found` | 404 | descriptivo |
| `roles.delete.transaction_failed` | 500 | genérico |
| `roles.update.error` | 500 | genérico |
| `roles.update.fields_required` | 400 | descriptivo |
| `roles.update.id_required` | 400 | descriptivo |
| `roles.update.not_found` | 404 | descriptivo |

## security_limits

| Scope | HTTP | Message |
|-------|------|---------|
| `security_limits.invalid_durations` | — | descriptivo |
| `security_limits.invalid_field` | — | descriptivo |
| `security_limits.out_of_range` | — | descriptivo |

## session_security

| Scope | HTTP | Message |
|-------|------|---------|
| `session_security.invalid_field` | — | descriptivo |
| `session_security.invalid_value` | — | descriptivo |
| `session_security.lookup_error` | 503 | genérico |

## sessions

| Scope | HTTP | Message |
|-------|------|---------|
| `sessions.limit_reached` | 409 | descriptivo |
| `sessions.list.error` | 500 | genérico |
| `sessions.list.invalid_token` | 401 | descriptivo |
| `sessions.list.missing_token` | 401 | descriptivo |
| `sessions.list.user_id_missing` | 401 | descriptivo |
| `sessions.list.user_id_required` | 400 | descriptivo |
| `sessions.revoke.error` | 500 | genérico |
| `sessions.revoke.id_required` | 400 | descriptivo |
| `sessions.revoke.invalid_token` | 401 | descriptivo |
| `sessions.revoke.missing_token` | 401 | descriptivo |
| `sessions.revoke.not_found` | 404 | descriptivo |
| `sessions.revoke.user_id_missing` | 401 | descriptivo |
| `sessions.unavailable` | 500 | genérico |

## system

| Scope | HTTP | Message |
|-------|------|---------|
| `system.api_key_pepper.error` | 500 | genérico |
| `system.encryption_status.error` | 500 | genérico |
| `system.outbox.error` | 500 | genérico |

## tenant

| Scope | HTTP | Message |
|-------|------|---------|
| `tenant.app_required` | 400 | descriptivo |
| `tenant.app_unresolved` | 401 | descriptivo |

## testers

| Scope | HTTP | Message |
|-------|------|---------|
| `testers.confirm_required` | 422 | descriptivo |
| `testers.disabled` | 422 | descriptivo |
| `testers.email_taken` | 409 | descriptivo |
| `testers.error_generating_tokens` | 500 | genérico |
| `testers.error_hashing_password` | 500 | genérico |
| `testers.error_saving` | 500 | genérico |
| `testers.expired` | 403 | descriptivo |
| `testers.id_required` | 400 | descriptivo |
| `testers.invalid_input` | 422 | descriptivo |
| `testers.job_not_found` | 404 | descriptivo |
| `testers.jobs_stopped` | 503 | genérico |
| `testers.lookup_error` | 500 | genérico |
| `testers.not_found` | 404 | descriptivo |
| `testers.password_managed` | 409 | descriptivo |
| `testers.password_policy` | 422 | descriptivo |
| `testers.role_locked` | 409 | descriptivo |
| `testers.username_taken` | 409 | descriptivo |

## totp

| Scope | HTTP | Message |
|-------|------|---------|
| `totp.backup_codes.invalid_code` | 401 | descriptivo |
| `totp.backup_codes.invalid_token` | 401 | descriptivo |
| `totp.backup_codes.missing_user_id` | 401 | descriptivo |
| `totp.backup_codes.totp_not_enabled` | 409 | descriptivo |
| `totp.backup_codes.transaction_failed` | 500 | genérico |
| `totp.backup_codes.unavailable` | 503 | genérico |
| `totp.backup_codes.user_not_found` | 404 | descriptivo |
| `totp.disable.failed` | 500 | genérico |
| `totp.disable.invalid_code` | 401 | descriptivo |
| `totp.disable.invalid_token` | 401 | descriptivo |
| `totp.disable.missing_user_id` | 401 | descriptivo |
| `totp.disable.transaction_failed` | 500 | genérico |
| `totp.disable.user_not_found` | 404 | descriptivo |
| `totp.qr.already_enabled` | 409 | descriptivo |
| `totp.qr.invalid_token` | 401 | descriptivo |
| `totp.qr.missing_user_id` | 401 | descriptivo |
| `totp.qr.not_configured` | 404 | descriptivo |
| `totp.qr.render_failed` | 500 | genérico |
| `totp.qr.user_not_found` | 404 | descriptivo |
| `totp.setup.already_enabled` | 409 | descriptivo |
| `totp.setup.generation_failed` | 500 | genérico |
| `totp.setup.invalid_token` | 401 | descriptivo |
| `totp.setup.missing_user_id` | 401 | descriptivo |
| `totp.setup.save_failed` | 500 | genérico |
| `totp.setup.user_not_found` | 404 | descriptivo |
| `totp.verify.enable_failed` | 500 | genérico |
| `totp.verify.invalid_code` | 401 | descriptivo |
| `totp.verify.invalid_token` | 401 | descriptivo |
| `totp.verify.missing_user_id` | 401 | descriptivo |
| `totp.verify.not_configured` | 400 | descriptivo |
| `totp.verify.transaction_failed` | 500 | genérico |
| `totp.verify.user_not_found` | 404 | descriptivo |

## user_metadata_policy

| Scope | HTTP | Message |
|-------|------|---------|
| `user_metadata_policy.app_id_required` | 400 | descriptivo |
| `user_metadata_policy.get.db` | 500 | genérico |
| `user_metadata_policy.preview.db` | 500 | genérico |
| `user_metadata_policy.preview.invalid_body` | 400 | descriptivo |
| `user_metadata_policy.put.invalid_body` | 400 | descriptivo |
| `user_metadata_policy.upsert.db` | 500 | genérico |
| `user_metadata_policy.upsert.key_too_long` | 400 | descriptivo |
| `user_metadata_policy.upsert.reserved_claim` | 400 | descriptivo |

## users

| Scope | HTTP | Message |
|-------|------|---------|
| `users.admin_auth.email_not_found` | 404 | descriptivo |
| `users.admin_auth.forbidden` | 403 | descriptivo |
| `users.admin_auth.hash_error` | 500 | genérico |
| `users.admin_auth.login_method_not_found` | 404 | descriptivo |
| `users.admin_auth.password_required` | 422 | descriptivo |
| `users.admin_auth.password_too_long` | 422 | descriptivo |
| `users.admin_auth.password_too_short` | 422 | descriptivo |
| `users.admin_auth.update_error` | 500 | genérico |
| `users.change_email.app_id_mismatch` | 401 | descriptivo |
| `users.change_email.code_not_found` | 404 | descriptivo |
| `users.change_email.code_not_valid` | 401 | descriptivo |
| `users.change_email.email_already_exists` | 409 | descriptivo |
| `users.change_email.error_checking_email` | 500 | genérico |
| `users.change_email.error_finding_user` | 500 | genérico |
| `users.change_email.error_generating_code` | 500 | genérico |
| `users.change_email.error_generating_token` | 500 | genérico |
| `users.change_email.error_getting_code` | 500 | genérico |
| `users.change_email.error_marking_code_as_removed` | 500 | genérico |
| `users.change_email.error_saving_code` | 500 | genérico |
| `users.change_email.error_searching_email` | 500 | genérico |
| `users.change_email.error_updating_email` | 500 | genérico |
| `users.change_email.invalid_code` | 401 | descriptivo |
| `users.change_email.invalid_token` | 401 | descriptivo |
| `users.change_email.invalid_token_format` | 401 | descriptivo |
| `users.change_email.rate_limited` | 429 | descriptivo |
| `users.change_email.too_many_attempts` | — | descriptivo |
| `users.change_email.unsupported_entity_type` | 400 | descriptivo |
| `users.change_email.user_id_mismatch` | 401 | descriptivo |
| `users.change_password.transaction_failed` | 500 | genérico |
| `users.change_password.unauthorized` | 401 | descriptivo |
| `users.create.error_matching_role` | 500 | genérico |
| `users.create.error_saving_user` | 500 | genérico |
| `users.create.role_not_found` | 404 | descriptivo |
| `users.create.transaction_failed` | 500 | genérico |
| `users.delete.code` | 500 | genérico |
| `users.delete.codes` | 500 | genérico |
| `users.delete.email` | 500 | genérico |
| `users.delete.email_codes` | 500 | genérico |
| `users.delete.emails` | 500 | genérico |
| `users.delete.forbidden` | 403 | descriptivo |
| `users.delete.invalid_token` | 401 | descriptivo |
| `users.delete.invalid_token_payload` | 401 | descriptivo |
| `users.delete.login_method` | 500 | genérico |
| `users.delete.login_methods` | 500 | genérico |
| `users.delete.magic_links` | 500 | genérico |
| `users.delete.missing_token` | 401 | descriptivo |
| `users.delete.oauth_login` | 500 | genérico |
| `users.delete.oauth_logins` | 500 | genérico |
| `users.delete.publish_event` | 500 | genérico |
| `users.delete.refresh_token` | 500 | genérico |
| `users.delete.refresh_tokens` | 500 | genérico |
| `users.delete.transaction_failed` | 500 | genérico |
| `users.delete.user` | 500 | genérico |
| `users.get.error` | 500 | genérico |
| `users.get.not_found` | 404 | descriptivo |
| `users.list.error_getting_users` | 500 | genérico |
| `users.list.invalid_filter` | 422 | descriptivo |
| `users.list.invalid_is_test` | 400 | descriptivo |
| `users.list.invalid_pagination` | 400 | descriptivo |
| `users.list.invalid_sort` | 422 | descriptivo |
| `users.list.search_unavailable` | 500 | genérico |
| `users.set_password.transaction_failed` | 500 | genérico |
| `users.testers.invalid_status` | 400 | descriptivo |
| `users.update_metadata.forbidden` | 403 | descriptivo |
| `users.update_metadata.get_user` | 500 | genérico |
| `users.update_metadata.schema_validation` | 422 | descriptivo |
| `users.update_metadata.transaction_failed` | 500 | genérico |
| `users.update_metadata.update` | 500 | genérico |
| `users.update_role.forbidden` | 403 | descriptivo |
| `users.update_role.get_user` | 500 | genérico |
| `users.update_role.role_not_found` | 404 | descriptivo |
| `users.update_role.transaction_failed` | 500 | genérico |
| `users.update_role.update` | 500 | genérico |
| `users.verify_email.transaction_failed` | 500 | genérico |

## webhooks

| Scope | HTTP | Message |
|-------|------|---------|
| `webhooks.create.error_creating_webhook` | 500 | genérico |
| `webhooks.create.invalid_events` | 400 | descriptivo |
| `webhooks.delete.error` | 500 | genérico |
| `webhooks.delete.id_required` | 400 | descriptivo |
| `webhooks.delete.not_found` | 404 | descriptivo |
| `webhooks.deliveries.error` | 500 | genérico |
| `webhooks.deliveries.id_required` | 400 | descriptivo |
| `webhooks.deliveries.not_found` | 404 | descriptivo |
| `webhooks.deliveries.unavailable` | 500 | genérico |
| `webhooks.list.error_listing_webhooks` | 500 | genérico |
| `webhooks.managed_externally` | 410 | descriptivo |
| `webhooks.set_active.error` | 500 | genérico |
| `webhooks.set_active.not_found` | 404 | descriptivo |
| `webhooks.set_active.update_error` | 500 | genérico |
| `webhooks.test.id_required` | 400 | descriptivo |
| `webhooks.test.not_found` | 404 | descriptivo |
| `webhooks.test.unreachable` | 502 | genérico |
| `webhooks.test.unsupported_event` | 422 | descriptivo |
| `webhooks.update.error` | 500 | genérico |
| `webhooks.update.fields_required` | 400 | descriptivo |
| `webhooks.update.id_required` | 400 | descriptivo |
| `webhooks.update.invalid_events` | 400 | descriptivo |
| `webhooks.update.not_found` | 404 | descriptivo |
| `webhooks.url.*` | 422 | descriptivo |

## Sin prefijo (históricos)

| Scope | HTTP | Message |
|-------|------|---------|
| `api_key_invalid` | 401 | genérico (seguridad) |
| `api_key_invalid_format` | 401 | descriptivo |
| `api_key_is_required` | 401 | descriptivo |
| `api_key_not_found` | 401 | genérico (seguridad) |
| `app_behavior_not_found` | 404 | descriptivo |
| `app_id_is_required` | 400 | descriptivo |
| `error_getting_api_key` | 500 | genérico |
| `error_getting_app_behaviors` | 500 | genérico |
| `error_getting_apps` | 500 | genérico |
| `error_getting_policies` | 500 | genérico |
| `error_getting_roles` | 500 | genérico |
| `error_updating_app` | 500 | genérico |
| `generate_api_key_error` | 500 | genérico |
| `hash_api_key_error` | 500 | genérico |
| `id_required` | 400 | descriptivo |
| `jwt_public_key_find_error` | 500 | genérico |
| `jwt_public_key_not_found` | 404 | descriptivo |
| `jwt_public_key_save_error` | 500 | genérico |
| `mutation_event` | 500 | genérico |
| `oauth_native_audiences` | 500 | genérico |
| `redirect_urls` | 500 | genérico |
| `save_api_key_error` | 500 | genérico |
| `secret_hash_missing` | 500 | genérico |
| `webhook_id_is_required` | 400 | descriptivo |

## client (componentes embebidos)

No los devuelve la API: los genera el SDK de [Embedded Auth](embedded-auth.md) en el navegador (`ui/src/core/errors.ts`) cuando no hay respuesta que mapear. Una respuesta sin `error.scope` llega como `http.<status>`.

| Scope |
|-------|
| `client.aborted` |
| `client.bad_request` |
| `client.components_unavailable` |
| `client.crypto_unavailable` |
| `client.invalid_response` |
| `client.invalid_token` |
| `client.magic_link_other_browser` |
| `client.mfa_enrollment_required` |
| `client.mfa_required` |
| `client.network_error` |
| `client.not_configured` |
| `client.oauth_provider_unavailable` |
| `client.offline` |
| `client.popup_blocked` |
| `client.popup_closed` |
| `client.popup_superseded` |
| `client.popup_timeout` |
| `client.request_failed` |
| `client.timeout` |

