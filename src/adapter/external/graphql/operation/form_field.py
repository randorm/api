from __future__ import annotations

from collections.abc import Iterable
from re import compile as re_compile

import strawberry as sb

import src.adapter.external.graphql.type.form_field as graphql
import src.domain.model as domain
import src.protocol.internal.database.form_field as proto
from src.adapter.external.graphql import scalar
from src.adapter.external.graphql.tool.context import Info
from src.adapter.external.graphql.tool.permission import DefaultPermissions
from src.adapter.external.graphql.type import format_entity
from src.utils.logger.logger import Logger

log = Logger("graphql-form-ops")


@sb.input
class SpoilerEntityInput(format_entity.SpoilerEntityType): ...


@sb.input
class BoldEntityInput(format_entity.BoldEntityType): ...


@sb.input
class ItalicEntityInput(format_entity.ItalicEntityType): ...


@sb.input
class MonospaceEntityInput(format_entity.MonospaceEntityType): ...


@sb.input
class LinkEntityInput(format_entity.LinkEntityType): ...


@sb.input
class StrikethroughEntityInput(format_entity.StrikethroughEntityType): ...


@sb.input
class UnderlineEntityInput(format_entity.UnderlineEntityType): ...


@sb.input
class CodeEntityInput(format_entity.CodeEntityType): ...


@sb.input
class FormatEntityInput:
    spoiler: SpoilerEntityInput | None = None
    bold: BoldEntityInput | None = None
    italic: ItalicEntityInput | None = None
    monospace: MonospaceEntityInput | None = None
    link: LinkEntityInput | None = None
    strikethrough: StrikethroughEntityInput | None = None
    underline: UnderlineEntityInput | None = None
    code: CodeEntityInput | None = None

    def to_domain(self) -> domain.FormatEntity:
        if self.spoiler:
            return domain.SpoilerEntity.model_validate(self.spoiler)
        if self.bold:
            return domain.BoldEntity.model_validate(self.bold)
        if self.italic:
            return domain.ItalicEntity.model_validate(self.italic)
        if self.monospace:
            return domain.MonospaceEntity.model_validate(self.monospace)
        if self.link:
            return domain.LinkEntity.model_validate(self.link)
        if self.strikethrough:
            return domain.StrikethroughEntity.model_validate(self.strikethrough)
        if self.underline:
            return domain.UnderlineEntity.model_validate(self.underline)
        if self.code:
            return domain.CodeEntity.model_validate(self.code)

        raise ValueError("No format entity provided")


def format_entities_to_domain_set(
    question_entities: Iterable[FormatEntityInput],  # type: ignore
) -> set[domain.FormatEntity]:
    return {entity.to_domain() for entity in question_entities}


@sb.experimental.pydantic.input(model=domain.ChoiceOption, all_fields=True)
class ChoiceOptionInput: ...


def choice_option_to_domain_list(
    options: Iterable[ChoiceOptionInput],
) -> list[domain.ChoiceOption]:  # type: ignore
    return [domain.ChoiceOption.model_validate(option) for option in options]


@sb.experimental.pydantic.input(model=proto.UpdateChoiceOption, all_fields=True)
class UpdateChoiceOptionInput: ...


def update_choice_option_to_proto_list(
    options: Iterable[UpdateChoiceOptionInput | None],
) -> list[proto.UpdateChoiceOption | None]:
    return [
        proto.UpdateChoiceOption.model_validate(option) if option else None
        for option in options
    ]


@sb.type
class FormFieldQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def form_field(
        root: FormFieldQuery, info: Info[FormFieldQuery], id: scalar.ObjectID
    ) -> graphql.FormFieldType:  # type: ignore
        with log.activity(f"loading form field {id}"):
            return await info.context.form_field.loader.load(id)


@sb.type
class AnswerQuery:
    @sb.field(permission_classes=[DefaultPermissions])
    async def answer(
        root: AnswerQuery, info: Info[AnswerQuery], id: scalar.ObjectID
    ) -> graphql.AnswerType:  # type: ignore
        with log.activity(f"loading answer {id}"):
            return await info.context.answer.loader.load(id)


@sb.type
class FormFieldMutation:
    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_text_form_field(
        root: FormFieldMutation,
        info: Info[FormFieldMutation],
        creator_id: scalar.ObjectID,
        question: str,
        required: bool,
        frozen: bool,
        question_entities: list[FormatEntityInput] | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
        re: str | None = None,
        ex: str | None = None,
    ) -> graphql.TextFormFieldType:
        with log.activity("creating new text form field"):
            request = proto.CreateTextFormField(
                creator_id=creator_id,
                question=question,
                required=required,
                frozen=frozen,
                question_entities=(
                    format_entities_to_domain_set(question_entities)
                    if question_entities
                    else set()
                ),
                editors_ids=set(editors_ids) if editors_ids else set(),
                re=re_compile(re) if re else None,
                ex=ex,
            )

            data = await info.context.form_field.service.create(request)
            log.info(f"created text form field {data.id}")
            return graphql.domain_to_form_field(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_choice_form_field(
        root: FormFieldMutation,
        info: Info[FormFieldMutation],
        creator_id: scalar.ObjectID,
        question: str,
        required: bool,
        frozen: bool,
        multiple: bool,
        options: list[ChoiceOptionInput],
        question_entities: list[FormatEntityInput] | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.ChoiceFormFieldType:
        with log.activity("creating new choice form field"):
            request = proto.CreateChoiceFormField(
                creator_id=creator_id,
                question=question,
                required=required,
                frozen=frozen,
                multiple=multiple,
                options=choice_option_to_domain_list(options),
                question_entities=(
                    format_entities_to_domain_set(question_entities)
                    if question_entities
                    else set()
                ),
                editors_ids=set(editors_ids) if editors_ids else set(),
            )

            data = await info.context.form_field.service.create(request)
            log.info(f"created choice form field {data.id}")
            return graphql.domain_to_form_field(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_text_form_field(
        root: FormFieldMutation,
        info: Info[FormFieldMutation],
        id: scalar.ObjectID,
        question: str | None = None,
        required: bool | None = None,
        frozen: bool | None = None,
        question_entities: list[FormatEntityInput] | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
        re: str | None = None,
        ex: str | None = None,
    ) -> graphql.TextFormFieldType:
        with log.activity(f"updating text form field {id}"):
            request = proto.UpdateTextFormField(
                _id=id,
                question=question,
                required=required,
                frozen=frozen,
                question_entities=(
                    format_entities_to_domain_set(question_entities)
                    if question_entities
                    else set()
                ),
                editors_ids=set(editors_ids) if editors_ids else set(),
                re=re_compile(re) if re else None,
                ex=ex,
            )

            data = await info.context.form_field.service.update(request)
            info.context.form_field.loader.clear(id)
            log.info(f"updated text form field {id}")
            return graphql.domain_to_form_field(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_choice_form_field(
        root: FormFieldMutation,
        info: Info[FormFieldMutation],
        id: scalar.ObjectID,
        question: str | None = None,
        required: bool | None = None,
        frozen: bool | None = None,
        multiple: bool | None = None,
        options: list[UpdateChoiceOptionInput | None] | None = None,
        question_entities: list[FormatEntityInput] | None = None,
        editors_ids: list[scalar.ObjectID] | None = None,
    ) -> graphql.ChoiceFormFieldType:
        with log.activity(f"updating choice form field {id}"):
            request = proto.UpdateChoiceFormField(
                _id=id,
                question=question,
                required=required,
                frozen=frozen,
                multiple=multiple,
                options=(
                    update_choice_option_to_proto_list(options) if options else None
                ),
                question_entities=(
                    format_entities_to_domain_set(question_entities)
                    if question_entities
                    else set()
                ),
                editors_ids=set(editors_ids) if editors_ids else set(),
            )

            data = await info.context.form_field.service.update(request)
            info.context.form_field.loader.clear(id)
            log.info(f"updated choice form field {id}")
            return graphql.domain_to_form_field(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_form_field(
        root: FormFieldMutation, info: Info[FormFieldMutation], id: scalar.ObjectID
    ) -> graphql.FormFieldType:  # type: ignore
        with log.activity(f"deleting form field {id}"):
            data = await info.context.form_field.service.delete(
                proto.DeleteFormField(_id=id)
            )
            info.context.form_field.loader.clear(id)
            log.info(f"deleted form field {id}")
            return graphql.domain_to_form_field(data)


@sb.type
class AnswerMutation:
    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_text_answer(
        root: AnswerMutation,
        info: Info[AnswerMutation],
        respondent_id: scalar.ObjectID,
        form_field_id: scalar.ObjectID,
        text: str,
        text_entities: list[FormatEntityInput] | None = None,
    ) -> graphql.AnswerType:  # type: ignore
        with log.activity("creating new text answer"):
            request = proto.CreateTextAnswer(
                respondent_id=respondent_id,
                form_field_id=form_field_id,
                text=text,
                text_entities=(
                    format_entities_to_domain_set(text_entities)
                    if text_entities
                    else set()
                ),
            )

            data = await info.context.answer.service.create(request)
            log.info(f"created text answer {data.id}")
            return graphql.domain_to_answer(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def new_choice_answer(
        root: AnswerMutation,
        info: Info[AnswerMutation],
        respondent_id: scalar.ObjectID,
        form_field_id: scalar.ObjectID,
        option_indexes: list[int],
    ) -> graphql.AnswerType:  # type: ignore
        with log.activity("creating new choice answer"):
            request = proto.CreateChoiceAnswer(
                respondent_id=respondent_id,
                form_field_id=form_field_id,
                option_indexes=set(option_indexes),
            )

            data = await info.context.answer.service.create(request)
            log.info(f"created choice answer {data.id}")
            return graphql.domain_to_answer(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_text_answer(
        root: AnswerMutation,
        info: Info[AnswerMutation],
        id: scalar.ObjectID,
        text: str | None = None,
        text_entities: list[FormatEntityInput] | None = None,
    ) -> graphql.AnswerType:  # type: ignore
        with log.activity(f"updating text answer {id}"):
            request = proto.UpdateTextAnswer(
                _id=id,
                text=text,
                text_entities=(
                    format_entities_to_domain_set(text_entities)
                    if text_entities
                    else set()
                ),
            )

            data = await info.context.answer.service.update(request)
            info.context.answer.loader.clear(id)
            log.info(f"updated text answer {id}")
            return graphql.domain_to_answer(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def update_choice_answer(
        root: AnswerMutation,
        info: Info[AnswerMutation],
        id: scalar.ObjectID,
        option_indexes: list[int] | None = None,
    ) -> graphql.AnswerType:  # type: ignore
        with log.activity(f"updating choice answer {id}"):
            request = proto.UpdateChoiceAnswer(
                _id=id,
                option_indexes=set(option_indexes) if option_indexes else None,
            )

            data = await info.context.answer.service.update(request)
            info.context.answer.loader.clear(id)
            log.info(f"updated choice answer {id}")
            return graphql.domain_to_answer(data)

    @sb.mutation(permission_classes=[DefaultPermissions])
    async def delete_answer(
        root: AnswerMutation, info: Info[AnswerMutation], id: scalar.ObjectID
    ) -> graphql.AnswerType:  # type: ignore
        with log.activity(f"deleting answer {id}"):
            data = await info.context.answer.service.delete(proto.DeleteAnswer(_id=id))
            info.context.answer.loader.clear(id)
            log.info(f"deleted answer {id}")
            return graphql.domain_to_answer(data)
