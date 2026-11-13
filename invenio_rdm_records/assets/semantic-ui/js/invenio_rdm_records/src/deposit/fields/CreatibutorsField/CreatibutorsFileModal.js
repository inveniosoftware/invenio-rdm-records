/*
 * SPDX-FileCopyrightText: 2026 CERN.
 * SPDX-License-Identifier: MIT
 */

import { Component, createRef } from "react";
import PropTypes from "prop-types";
import { Button, Header, Icon, Message, Modal, Segment, Tab } from "semantic-ui-react";
import { i18next } from "@translations/invenio_rdm_records/i18next";
import {
  normalizeCreatibutorFileEntry,
  validateCreatibutorEntry,
} from "./CreatibutorsModal";
import { CreatibutorsInlinePanel } from "./CreatibutorsDisplay/CreatibutorsInlinePanel";
import { CreatibutorsItemContext } from "./CreatibutorsFieldItem";
import { CREATIBUTOR_FILE_ERROR, parseCreatibutorFile } from "./parseCreatibutorFile";
import {
  creatibutorFileFormatPropType,
  getCreatibutorFileFormats,
} from "./fileFormats";

const getCreatibutorSchemaLabel = (schema) =>
  schema === "creators" ? "authors/creators" : "contributors";

const fileExtensions = (formats) => formats.map((format) => format.extension);

// Format labels and notes are translated by whoever registers the format.
const getParseErrorMessage = (error) => {
  switch (error.type) {
    case CREATIBUTOR_FILE_ERROR.UNSUPPORTED:
      return i18next.t("This file type is not supported.");
    case CREATIBUTOR_FILE_ERROR.INVALID:
      return i18next.t("This is not a valid {{format}} file.", {
        format: error.format,
        interpolation: { escapeValue: false },
      });
    default:
      return null;
  }
};

const fileFormatPane = (format) => ({
  menuItem: format.label,
  render: () => (
    <Tab.Pane attached={false}>
      {format.example && (
        <pre className="creatibutors-import-example">{format.example}</pre>
      )}
      {format.note && <p className="text-muted mb-0">{format.note}</p>}
    </Tab.Pane>
  ),
});

const FileFormatExamples = ({ fileFormats }) => {
  const panes = fileFormats
    .filter((format) => format.example || format.note)
    .map(fileFormatPane);

  if (panes.length === 0) return null;
  return <Tab menu={{ secondary: true, pointing: true }} panes={panes} />;
};

FileFormatExamples.propTypes = {
  fileFormats: PropTypes.arrayOf(creatibutorFileFormatPropType).isRequired,
};

function CreatibutorsFileImport({
  schema,
  fileFormats,
  loading,
  fileInputRef,
  onFileChange,
  onTriggerFileInput,
}) {
  const type = getCreatibutorSchemaLabel(schema);
  const extensions = fileExtensions(fileFormats);

  const handleDragOver = (e) => {
    e.preventDefault();
    e.stopPropagation();
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (loading) return;
    const { files } = e.dataTransfer;
    if (files && files.length > 0) {
      onFileChange({ target: { files } });
    }
  };

  return (
    <>
      <Segment
        placeholder
        textAlign="center"
        className={`mt-0 file-import-dropzone${
          loading ? " file-import-dropzone--loading" : ""
        }`}
        onDragOver={handleDragOver}
        onDrop={handleDrop}
      >
        <Header icon>
          <Icon name="cloud upload" />
          {i18next.t(`Upload ${type} from file`)}
          <Header.Subheader>
            {i18next.t("Supported file types: {{ extensions }}", {
              extensions: extensions.join(", "),
            })}
          </Header.Subheader>
        </Header>
        <Button
          primary
          type="button"
          loading={loading}
          disabled={loading}
          onClick={onTriggerFileInput}
        >
          <Icon name="folder open outline" />
          {i18next.t("Choose file")}
        </Button>
        <div className="mt-15 text-muted">{i18next.t("Or drag a file here")}</div>
        <input
          type="file"
          hidden
          ref={fileInputRef}
          accept={extensions.join(",")}
          onChange={onFileChange}
        />
      </Segment>

      <Message info size="small" className="text-left mt-15">
        <Message.Header>{i18next.t("File format")}</Message.Header>
        <p>
          {schema === "creators"
            ? i18next.t("Upload a file containing a list of authors/creators.")
            : i18next.t("Upload a file containing a list of contributors.")}
        </p>
        <FileFormatExamples fileFormats={fileFormats} />
      </Message>
    </>
  );
}

CreatibutorsFileImport.propTypes = {
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  fileFormats: PropTypes.arrayOf(creatibutorFileFormatPropType).isRequired,
  loading: PropTypes.bool.isRequired,
  fileInputRef: PropTypes.object.isRequired,
  onFileChange: PropTypes.func.isRequired,
  onTriggerFileInput: PropTypes.func.isRequired,
};

function CreatibutorsFileReview({
  schema,
  fileFormats,
  fileName = null,
  parseError = null,
  validEntries,
  invalidEntries,
  onRemove,
  onReplace,
  onMove,
  roleOptions,
  autocompleteNames = "search",
  addLabel = undefined,
  editLabel = undefined,
  serializeSuggestions = undefined,
  serializeCreatibutor = undefined,
  deserializeCreatibutor = undefined,
}) {
  const type = getCreatibutorSchemaLabel(schema);

  return (
    <>
      <Message size="small">
        <Icon name="file outline" />
        <strong>{fileName}</strong>
      </Message>

      {parseError ? (
        <Message error size="small">
          <Message.Header>
            <Icon name="exclamation triangle" />
            {getParseErrorMessage(parseError)}
          </Message.Header>
          <p>{i18next.t("Please upload a file in one of the supported formats:")}</p>
          <FileFormatExamples fileFormats={fileFormats} />
        </Message>
      ) : (
        <>
          {validEntries.length > 0 && (
            <>
              <Header as="h4" className="mb-10">
                {i18next.t(`Valid ${type} (${validEntries.length})`)}
              </Header>
              <CreatibutorsItemContext.Provider
                value={{
                  roleOptions,
                  schema,
                  autocompleteNames,
                  addLabel,
                  editLabel,
                  serializeSuggestions,
                  serializeCreatibutor,
                  deserializeCreatibutor,
                }}
              >
                <CreatibutorsInlinePanel
                  type={type}
                  list={validEntries}
                  keyPrefix="fileImport"
                  removeCreatibutor={onRemove}
                  replaceCreatibutor={onReplace}
                  moveCreatibutor={onMove}
                />
              </CreatibutorsItemContext.Provider>
            </>
          )}

          {invalidEntries.length > 0 && (
            <Message error size="small">
              <Message.Header>
                <Icon name="exclamation triangle" />
                {i18next.t("{{count}} entries could not be imported", {
                  count: invalidEntries.length,
                })}
              </Message.Header>
              <Message.List numbered>
                {invalidEntries.map((inv, idx) => {
                  const preview =
                    typeof inv.raw === "string" ? inv.raw : JSON.stringify(inv.raw);
                  return (
                    <Message.Item key={inv.reason}>
                      <code>{preview}</code> {inv.reason}
                    </Message.Item>
                  );
                })}
              </Message.List>
            </Message>
          )}

          {validEntries.length === 0 && invalidEntries.length === 0 && (
            <Message info size="small">
              <Icon name="info circle" />
              {i18next.t("The file appears to be empty.")}
            </Message>
          )}
        </>
      )}
    </>
  );
}

CreatibutorsFileReview.propTypes = {
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  fileFormats: PropTypes.arrayOf(creatibutorFileFormatPropType).isRequired,
  fileName: PropTypes.string,
  parseError: PropTypes.shape({
    type: PropTypes.oneOf(Object.values(CREATIBUTOR_FILE_ERROR)).isRequired,
    format: PropTypes.string,
  }),
  validEntries: PropTypes.array.isRequired,
  invalidEntries: PropTypes.array.isRequired,
  onRemove: PropTypes.func.isRequired,
  onReplace: PropTypes.func.isRequired,
  onMove: PropTypes.func.isRequired,
  roleOptions: PropTypes.array.isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
};

export class CreatibutorsFileModal extends Component {
  constructor(props) {
    super(props);
    this.state = {
      open: false,
      phase: "pick",
      loading: false,
      fileName: null,
      validEntries: [],
      invalidEntries: [],
      parseError: null,
    };
    this.fileInputRef = createRef();
  }

  openModal = () => {
    this.setState({
      open: true,
      phase: "pick",
      loading: false,
      fileName: null,
      validEntries: [],
      invalidEntries: [],
      parseError: null,
    });
  };

  closeModal = () => {
    this.setState({ open: false });
  };

  resetToCreatibutorsFileImport = () => {
    this.setState({
      phase: "pick",
      validEntries: [],
      invalidEntries: [],
      parseError: null,
    });
  };

  triggerFileInput = () => {
    if (this.fileInputRef.current) {
      this.fileInputRef.current.value = null;
      this.fileInputRef.current.click();
    }
  };

  handleFileChange = (event) => {
    const fileFormats = getCreatibutorFileFormats();
    const file = event.target.files[0];
    if (!file) return;
    this.setState({ loading: true });
    const reader = new FileReader();
    reader.onload = (e) => {
      const result = parseCreatibutorFile(e.target.result, file.name, fileFormats);
      this.classifyEntries(result, file.name);
    };
    reader.onerror = () => {
      this.setState({ loading: false });
    };
    reader.readAsText(file);
  };

  classifyEntries = (result, fileName) => {
    if (result.error) {
      this.setState({
        loading: false,
        fileName,
        validEntries: [],
        invalidEntries: [],
        parseError: result.error,
        phase: "review",
      });
      return;
    }

    const validEntries = [];
    const invalidEntries = [];
    result.entries.forEach((raw) => {
      const entry = normalizeCreatibutorFileEntry(raw);
      const error = validateCreatibutorEntry(entry);
      if (error) {
        invalidEntries.push({ raw, reason: error });
      } else {
        validEntries.push(entry);
      }
    });
    this.setState({
      loading: false,
      fileName,
      validEntries,
      invalidEntries,
      parseError: null,
      phase: "review",
    });
  };

  localRemove = (index) => {
    this.setState((prev) => {
      const validEntries = [...prev.validEntries];
      validEntries.splice(index, 1);
      return { validEntries };
    });
  };

  localReplace = (index, newValue) => {
    this.setState((prev) => {
      const validEntries = [...prev.validEntries];
      validEntries[index] = newValue;
      return { validEntries };
    });
  };

  localMove = (from, to) => {
    this.setState((prev) => {
      const validEntries = [...prev.validEntries];
      const [item] = validEntries.splice(from, 1);
      validEntries.splice(to, 0, item);
      return { validEntries };
    });
  };

  handleConfirm = () => {
    const { onConfirm } = this.props;
    const { validEntries } = this.state;
    onConfirm(validEntries);
    this.closeModal();
  };

  render() {
    const {
      trigger,
      schema,
      roleOptions,
      autocompleteNames = "search",
      addLabel = undefined,
      editLabel = undefined,
      serializeSuggestions = undefined,
      serializeCreatibutor = undefined,
      deserializeCreatibutor = undefined,
    } = this.props;
    const acceptedFileFormats = getCreatibutorFileFormats();
    // Without a registered format there is nothing to import: offer no dialog.
    if (acceptedFileFormats.length === 0) return null;
    const { open, phase, loading, fileName, validEntries, invalidEntries, parseError } =
      this.state;
    const type = getCreatibutorSchemaLabel(schema);

    const headerText =
      phase === "pick"
        ? i18next.t(`Add ${type} from file`)
        : i18next.t(`Review ${type} from file`);

    return (
      <Modal
        onOpen={this.openModal}
        open={open}
        onClose={this.closeModal}
        trigger={trigger}
        size="large"
        closeOnDimmerClick={false}
        closeIcon
      >
        <Modal.Header as="h2" className="pt-10 pb-10">
          {headerText}
        </Modal.Header>

        <Modal.Content scrolling>
          {phase === "pick" ? (
            <CreatibutorsFileImport
              schema={schema}
              fileFormats={acceptedFileFormats}
              loading={loading}
              fileInputRef={this.fileInputRef}
              onFileChange={this.handleFileChange}
              onTriggerFileInput={this.triggerFileInput}
            />
          ) : (
            <CreatibutorsFileReview
              schema={schema}
              fileFormats={acceptedFileFormats}
              fileName={fileName}
              parseError={parseError}
              validEntries={validEntries}
              invalidEntries={invalidEntries}
              onRemove={this.localRemove}
              onReplace={this.localReplace}
              onMove={this.localMove}
              roleOptions={roleOptions}
              autocompleteNames={autocompleteNames}
              addLabel={addLabel}
              editLabel={editLabel}
              serializeSuggestions={serializeSuggestions}
              serializeCreatibutor={serializeCreatibutor}
              deserializeCreatibutor={deserializeCreatibutor}
            />
          )}
        </Modal.Content>

        <Modal.Actions>
          {phase === "review" && (
            <Button
              floated="left"
              type="button"
              icon="arrow left"
              content={i18next.t("Choose a different file")}
              onClick={this.resetToCreatibutorsFileImport}
            />
          )}
          <Button
            icon="close"
            content={i18next.t("Cancel")}
            type="button"
            onClick={this.closeModal}
          />
          {phase === "review" && (
            <Button
              positive
              type="button"
              icon="check"
              disabled={validEntries.length === 0}
              content={i18next.t(`Import ${validEntries.length} ${type}`)}
              onClick={this.handleConfirm}
            />
          )}
        </Modal.Actions>
      </Modal>
    );
  }
}

CreatibutorsFileModal.propTypes = {
  trigger: PropTypes.node.isRequired,
  schema: PropTypes.oneOf(["creators", "contributors"]).isRequired,
  onConfirm: PropTypes.func.isRequired,
  roleOptions: PropTypes.array.isRequired,
  autocompleteNames: PropTypes.oneOf(["search", "search_only", "off"]),
  addLabel: PropTypes.node,
  editLabel: PropTypes.node,
  serializeSuggestions: PropTypes.func,
  serializeCreatibutor: PropTypes.func,
  deserializeCreatibutor: PropTypes.func,
};
